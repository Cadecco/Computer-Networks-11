import socket
import threading
import time
import json
import random

class Packet:
    def __init__(self, chat_id, seq_number, data, is_final, ack=False, missing_packets=None):
        self.chat_id = chat_id
        self.seq_number = seq_number
        self.data = data
        self.is_final = is_final
        self.ack = ack
        self.missing_packets = missing_packets if missing_packets is not None else []

def main():
    host = '127.0.0.1'
    port = 61000
    server_addr = (host, port)

    id = random.randint(8000, 9000)

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        message = input("Enter Message: ")

        Message = (f"{id} : {message} ")

        client_socket.sendto(Message.encode(), server_addr)

        print("Sent message to server: {}".format(Message))
    
if __name__ == "__main__":
    main()
