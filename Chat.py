import threading
import handlers
import timeout
import server_processor

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

            server_processor.server_processor(packet)

    def chat_sender(self, packet):
        dec_pack = handlers.decode_packet(packet)
        self.sent_packets[dec_pack.seq_num] = dec_pack
        self.socket.sendto(packet, self.addr)
        self.timer_dict[dec_pack.seq_num] = timeout.timeout(self.addr, dec_pack.seq_num, self.ack_packets, self.sent_packets, self.socket)
