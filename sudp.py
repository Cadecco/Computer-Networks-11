import socket
import threading
import time
import handlers
import timeout


# Initialise array of chats.
chats = {}

# Declared globally here so that the server can be accessed by all the fucntions.
host = '0.0.0.0'
port = 61000

server_id = 1234

magic = 17109271

ack_packets = {}
sent_packets = {}
   
# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Chat:
    def __init__(self, addr, packet):
        self.addr = addr
        self.packet = packet
        self.client_id = packet.client_id
        self.checksum = packet.checksum
        self.data = packet.data
        self.buffer = [] 
        self.corrupted_count = 0
        self.incoming_lock = threading.Lock()  
        
        self.thread_number = threading.Thread(target=self.chat_receiver, args=(self.packet, ))
        self.thread_number.start()

        self.timer_dict = {}
        self.sent_packets = {}
        self.ack_packets = {}
        self.recv_packets = {}

    def chat_receiver(self, packet):
        with self.incoming_lock:

            if(self.corrupted_count > 2):
                client_kill(self.addr, self.client_id)
            
            if(packet.magic != magic):
                handlers.send_nack(server, self.addr, packet,server_id)

            corrupted = handlers.corruption_check(packet)
            if(corrupted):
                handlers.send_nack(server, self.addr, packet, server_id)
                self.corrupted_count = self.corrupted_count + 1

            if packet.type == 1:
                self.recv_packets[packet.seq_num] = packet
                print(f"")
                
            elif packet.type == 0:
            
                self.buffer.append(packet.data.decode())
                handlers.send_ack(server, self.addr, packet, server_id)
                self.recv_packets[packet.seq_num] = packet
            
                if len(self.buffer) > 0:
                        print(f"Received from ID {self.client_id}, {self.buffer[0]}")
                        self.buffer.pop(0)

    def chat_sender(self, packet):
        dec_pack = handlers.decode_packet(packet)
        self.sent_packets[dec_pack.seq_num] = dec_pack
        self.timer_dict[dec_pack.seq_num] = timeout.timeout(self.addr, dec_pack.seq_num, self.ack_packets, self.sent_packets, server)
        server.sendto(packet, self.addr)


def client_kill(addr, id):
    chats.pop(id)
    print(f"Client {id} Terminated")

def broadcast():
    for client in chats.values():
        id = client.client_id
        to_send = handlers.create_packet(magic, 1, 5, 0, 0, "AHHHHH")
        chats[id].chat_sender(to_send)
        
    print(f"Broadcast Sent")

def handle_client(addr, packet, chats):

    dec_pack = handlers.decode_packet(packet)
    chat_number = chats.get(dec_pack.client_id)

    # If there is a chat matching this ID send it to the SR ARQ handler.
    if chat_number:
        chats[dec_pack.client_id].chat_receiver(dec_pack)
        
    else:
        # If the chat doesn't exist 
        print(f"New Connecton from {addr} with ID: {dec_pack.client_id}")

        chats[dec_pack.client_id] = Chat(addr, dec_pack)
        # Send the packet.
        #chats[addr].chat_loop(data)
    print(f"Number of Clients: {len(chats)}")


def server_listener():
    
    # Bind the socket to the host and port
    server.bind((host, port))
    print("Server listening on {} : {}".format(host, port))

    while True:

        # Receiving the UDP packet.
        packet, addr = server.recvfrom(1024)   
        handle_client(addr, packet, chats)

def server_sender():

    while True:
        message = input("\nEnter Message: ")

        broadcast()
        print("Sent message to clients: {}".format(message))


def main():

    listen_thread = threading.Thread(target=server_listener, )
    listen_thread.start()

    send_thread = threading.Thread(target=server_sender, )
    send_thread.start()


if __name__ == "__main__":
    main()
