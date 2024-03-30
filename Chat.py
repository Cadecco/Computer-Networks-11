import threading
import handlers
import timeout

class Chat:
    def __init__(self, addr, packet, socket, server_id, magic):
        self.addr = addr
        self.packet = packet
        self.socket = socket
        self.client_id = packet.client_id
        self.checksum = packet.checksum
        self.data = packet.data
        self.server_id = server_id
        self.magic = magic
        self.buffer = [] 
        self.corrupted_count = 0
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
                handlers.send_nack(self.socket, self.addr, packet, self.server_id)

            corrupted = handlers.corruption_check(packet)
            if(corrupted):
                handlers.send_nack(self.socket, self.addr, packet, self.server_id)
                self.corrupted_count = self.corrupted_count + 1

            if packet.type == 1:
                self.ack_packets[packet.seq_num] = packet
                print(f"")
                
            elif packet.type == 0:
            
                self.buffer.append(packet.data.decode())
                #handlers.send_ack(self.socket, self.addr, packet, self.server_id)
                if not self.recv_packets.get(packet.seq_num):
                    self.recv_packets[packet.seq_num] = packet
            
                    if len(self.buffer) > 0:
                        print(f"Received from ID {self.client_id}, {self.buffer[0]}")
                        self.buffer.pop(0)

                else:
                    # If a packet has been received already procecss it as a duplicate.
                    print(f"Duplicate packet found {self.buffer[0]}")
                    self.buffer.pop(0)

    def chat_sender(self, packet):
        dec_pack = handlers.decode_packet(packet)
        self.sent_packets[dec_pack.seq_num] = dec_pack
        self.socket.sendto(packet, self.addr)
        self.timer_dict[dec_pack.seq_num] = timeout.timeout(self.addr, dec_pack.seq_num, self.ack_packets, self.sent_packets, self.socket)
