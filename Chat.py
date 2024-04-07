import threading
import handlers
import timeout
import globals

# Chat object for a particular client's connection to the server.
class Chat:
    def __init__(self, addr, packet, socket, server_id, magic, vote_manager):
        # Instantiate it with address, id etc...
        self.addr = addr
        self.packet = packet
        self.socket = socket
        self.vote_manager = vote_manager
        self.client_id = packet.client_id
        self.checksum = packet.checksum
        self.server_id = server_id
        self.magic = magic
        self.buffer = [] 
        self.corrupted_count = 0
        self.sequence = 0
        self.pack_num = 0
        self.connected = False
        self.features = []
        self.incoming_lock = threading.Lock()  

        self.timer_dict = {}
        self.sent_packets = {}
        self.ack_packets = {}
        self.recv_packets = {}
        
        self.thread_number = threading.Thread(target=self.chat_receiver, args=(self.packet, ))
        self.thread_number.start()


    # Start the receiver on one thread and direct all messages to the chat processor.
    def chat_receiver(self, packet):
        with self.incoming_lock:

            self.chat_processor(packet)

    # Start sender on another
    def chat_sender(self, packet):
        dec_pack = handlers.decode_packet(packet)
        self.sent_packets[dec_pack.pack_num] = dec_pack
        self.socket.sendto(packet, self.addr)

        # Only increment the sequence number for 'data' type packets.
        if dec_pack.type == 0:
            self.sequence = self.sequence + 1
        else:
            self.sequence = self.sequence


#-----------------------------------------------------------------------------------------------------------------------------------------#

    # Chat processor takes appropriate action depending on received packet.
    def chat_processor(self, packet):

        # Data
        if (packet.type == 0):
            if self.recv_packets.get(packet.pack_num) is not None: return

            # If a 'hello' packet is received print out the features of the client
            # send back a hello response packet.
            if packet.packet_id == 0:
                self.recv_packets[packet.pack_num] = packet
                print(f"Received Hello Packet from Client {packet.client_id} ")
                print(f"Client Features {packet.features}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                hello_response = handlers.create_hello_response(self.magic, self.client_id, 0, 0, True, 0, 1, packet.num_features, packet.features)
                self.features = packet.features
                self.chat_sender(hello_response)
                print(f"Sent Hello Response to {self.client_id}")

            # If vote request received, prepare a new poll for the question.
            elif packet.packet_id == 2:
                self.recv_packets[packet.pack_num] = packet
                print(f"Received Vote Request from Client: {packet.client_id} Question: {packet.question}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                self.vote_manager.prepare_poll(packet)
                #compute_answer(packet)

            # If received a response add this vote the appropriate poll using the vote manager.
            elif packet.packet_id == 4:
                self.recv_packets[packet.pack_num] = packet
                print(f"Received Resposne to Question from Client: {packet.client_id} {packet.vote_id}\n Response {packet.response}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                self.vote_manager.add_vote(packet)

            elif packet.packet_id == 6:

                if self.recv_packets.get(packet.pack_num):
                    print(f"Duplicate Received with Sequence No. {packet.pack_num}")
                else:
                    self.recv_packets[packet.pack_num] = packet
                    print(f"From Client {packet.client_id} : {packet.message}")
                    handlers.send_ack(self.socket, self.addr, packet, self.client_id)
            
            elif packet.packet_id == 0x12:
                self.recv_packets[packet.pack_num] = packet
                print(f"Received Client Packet: {packet.client_id}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)


        # ACK
        elif (packet.type == 3):
            print(f"SYN received")
            # Create a SYN ACK
            packet = handlers.create_ACK_NACK(packet.magic, self.client_id, 0, 0, 1, 4)
            self.chat_sender(packet)
            print(f"SENT SYNACK")

        # If received a ping from the client, send the pring response.
        elif (packet.type == 0xFFFE):
            print(f"\nReceived Ping")
            packet = handlers.create_ACK_NACK(packet.magic, self.client_id, 0, 0, 1, 0xFFFF)
            self.chat_sender(packet)

        elif (packet.type == 1):
            self.ack_packets[packet.pack_num] = packet
            if self.ack_packets.get(0) and self.connected == False:
                print(f"----------\nClient {self.client_id} has Officially Connected\nFeatures: {self.features}\n----------")
                self.connected = True

            print(f"From Client {packet.client_id}: ACK {packet.pack_num}")

        # NACK
        elif packet.type == 2:
            print(f"From Client {packet.client_id}: NACK {packet.pack_num}")