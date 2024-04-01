import threading
import handlers
import timeout

class Chat:
    def __init__(self, addr, packet, socket, server_id, magic, vote_manager):
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
        self.connected = False
        self.incoming_lock = threading.Lock()  

        self.timer_dict = {}
        self.sent_packets = {}
        self.ack_packets = {}
        self.recv_packets = {}
        
        self.thread_number = threading.Thread(target=self.chat_receiver, args=(self.packet, ))
        self.thread_number.start()


    def chat_receiver(self, packet):
        with self.incoming_lock:

            if(self.corrupted_count > 2):
               handlers.client_kill(self.addr, self.client_id)
            
            if(packet.magic != self.magic):
                print(f"{self.client_id} Magic Does Not Match")
                handlers.send_nack(self.socket, self.addr, packet, self.server_id)

            corrupted = handlers.corruption_check(packet)
            if(corrupted):
                print(f"{self.client_id} w/ Seq {packet.seq_num} Corrupted")
                handlers.send_nack(self.socket, self.addr, packet, self.server_id)
                self.corrupted_count = self.corrupted_count + 1

            else:
                self.chat_processor(packet)

    def chat_sender(self, packet):
        dec_pack = handlers.decode_packet(packet)
        self.sent_packets[dec_pack.seq_num] = dec_pack
        self.socket.sendto(packet, self.addr)
        self.timer_dict[dec_pack.seq_num] = timeout.timeout(self.addr, dec_pack.seq_num, self.ack_packets, self.sent_packets, self.socket)

        self.sequence = self.sequence + 1

#-----------------------------------------------------------------------------------------------------------------------------------------#

    def chat_processor(self, packet):

        # Data
        if (packet.type == 0):
            if packet.packet_id == 0:
                self.recv_packets[packet.seq_num] = packet
                print(f"Received Hello Packet from Client {packet.client_id} ")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                hello_response = handlers.create_hello_response(self.magic, self.client_id, self.sequence, True, 0, 1, packet.num_features, packet.features)
                self.chat_sender(hello_response)
                print(f"Sent Hello Response to {self.client_id}")

            elif packet.packet_id == 2:
                self.recv_packets[packet.seq_num] = packet
                print(f"Received Vote Request from Client: {packet.client_id} Question: {packet.question}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                self.vote_manager.prepare_poll(packet)
                #compute_answer(packet)

            elif packet.packet_id == 4:
                self.recv_packets[packet.seq_num] = packet
                print(f"Received Resposne to Question from Client: {packet.client_id} {packet.vote_id}\n Response {packet.response}")
                handlers.send_ack(self.socket, self.addr, packet, self.client_id)
                self.vote_manager.add_vote(packet)

            elif packet.packet_id == 6:

                if self.recv_packets.get(packet.seq_num):
                    print(f"Duplicate Received with Sequence No. {packet.seq_num}")
                else:
                    self.recv_packets[packet.seq_num] = packet
                    print(f"From Client {packet.client_id} : {packet.message}")
                    handlers.send_ack(self.socket, self.addr, packet, self.client_id)

        # ACK
        elif (packet.type == 1):
            self.ack_packets[packet.seq_num] = packet
            if self.ack_packets.get(0) and self.connected == False:
                print(f"----------\nClient {self.client_id} has Officially Connected\n----------")
                self.connected = True

            print(f"From Client {packet.client_id}: ACK {packet.seq_num}")

        # NACK
        elif packet.type == 2:
            print(f"From Client {packet.client_id}: NACK {packet.seq_num}")