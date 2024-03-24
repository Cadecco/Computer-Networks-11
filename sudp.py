import socket
import threading
import struct
import zlib

import handlers


# Initialise array of chats.
chats = {}

# Declared globally here so that the server can be accessed by all the fucntions.
host = '0.0.0.0'
port = 61000

magic = 17109271
   
# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_checksum(data):
    checksum = zlib.crc32(data)
    return checksum

def corruption_check(packet):
    correct_checksum = packet.checksum
    checksum = get_checksum(packet.data)
    corrupted = correct_checksum != checksum
    return corrupted

class Chat:
    def __init__(self, addr, packet):
        self.addr = addr
        self.packet = packet
        self.id = packet.id
        self.checksum = packet.checksum
        self.data = packet.data
        self.buffer = [] 
        self.incoming_lock = threading.Lock()  
        
        self.thread_number = threading.Thread(target=self.chat_loop, args=(self.packet, ))
        self.thread_number.start()
  
    def chat_loop(self, packet):
        with self.incoming_lock:
            self.buffer.append(packet.data.decode())

            handlers.send_ack(server, self.addr, packet)

            corrupted = corruption_check(packet)
            if(corrupted or packet.magic != magic):
                handlers.resend(server, self.addr, packet)

            
            if len(self.buffer) > 0:
                    print(f"Received from ID {self.id}, {self.buffer[0]}")
                    self.buffer.pop(0)


def handle_client(addr, packet, chats):

    dec_pack = handlers.decode_packet(packet)
    
    chat_number = chats.get(dec_pack.id)

    # If there is a chat matching this ID send it to the SR ARQ handler.
    if chat_number:
        chats[dec_pack.id].chat_loop(dec_pack)
        
    else:
        # If the chat doesn't exist 
        print(f"New Connecton from {addr} with ID: {dec_pack.id}")

        chats[dec_pack.id] = Chat(addr, dec_pack)

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

def main():
    server_listener()

if __name__ == "__main__":
    main()
