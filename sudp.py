import socket
import threading
import time
import json

# Initialise array of chats.
chats = {}

class Chat:
    def __init__(self, chat_id, server, data):
        self.chat_id = chat_id
        self.data = data

        self.buffer = [] 
        self.server = server
        self.incoming_lock = threading.Lock()  
        
        self.thread_number = threading.Thread(target=self.chat_loop, args=(data, ))
        self.thread_number.start()

  
    def chat_loop(self, data):
        with self.incoming_lock:
            self.buffer.append(data.decode())
            if len(self.buffer) > 0:
                    print(f"Received message {self.chat_id}, {self.buffer[0]}")
                    self.buffer.pop(0)


def handle_client(server_socket, addr, data, chats):
    
    chat_number = chats.get(addr)

    # If there is a chat matching this ID send it to the SR ARQ handler.
    if chat_number:
        chats[addr].chat_loop(data)

    else:
        # If the chat doesn't exist 
        print(f"New Connecton from{addr}")

        chats[addr] = Chat(addr, server_socket, data)

        # Send the packet.
        #chats[addr].chat_loop(data)

    print(f"Number of Clients: {len(chats)}")


def server_listener():
    host = '0.0.0.0'
    port = 61000
   
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the host and port
    server_socket.bind((host, port))
    print("Server listening on {} : {}".format(host, port))

    while True:

        data, addr = server_socket.recvfrom(1024)   
        handle_client(server_socket, addr, data, chats)

def main():
    server_listener()

if __name__ == "__main__":
    main()
