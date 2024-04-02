import socket
import random
import threading
import handlers
import timeout
import voting

#define MAGIC 17109271

host = '127.0.0.1'
port = 8080
# ID for this client, will not change once generated.
client_id = random.randint(8000, 9000)
magic = 17109271
sequence = 0
final = 0
type = 0

server_addr = (host, port)
# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(2)

exception = True     
sent_packets = {}
timeouts = {}
ack_packets = {}
recv_packets = {}
features = []
num_features = len(features)
connected = False

def startup_sequence():
    print(f"Enter Features to Add to this Client\n'1' For Simple Math Compute\n'3' For Just Messaging\n'5' For Defecting Vote")
    while True:
        feature_input = input()
        if feature_input == '1':
            features.append(int(feature_input))
            print(f"Feature added")
        elif feature_input == '3':
            features.append(int(feature_input))
            print(f"Feature Added")
        elif feature_input == '5':
            features.append(int(feature_input))
            print(f"Defecting Added")
        elif feature_input == "":
            break
        else:
            print(f"Invalid Feature Input, Try Again")

    print(f"Client Initialised With Features: {features}")   

    input(f"Press Any Key to Connect to the Server")

    sequence = 0

    packet = handlers.create_hello_packet(magic, client_id, sequence, sequence, 1, 0, 1, num_features, features)
    dec_pack = handlers.decode_packet(packet)
    sent_packets[dec_pack.pack_num] = dec_pack
    client_socket.sendto(packet, server_addr)
    print("Sent Hello Message to Server")
    start_timeout(dec_pack.pack_num)

    sequence = sequence + 1

def client_listener():
    global sequence
    lock = threading.Lock()
    while True:
        try:
            rec_pack, addr = client_socket.recvfrom(1024)
            received = handlers.decode_packet(rec_pack)
            with lock:
                client_processor(received)
        except:
            continue

def start_timeout(pack_num):
    timeouts[pack_num] = timeout.timeout(server_addr, pack_num, ack_packets, sent_packets, client_socket)
    #timeouts[pack_num].timeout_loop()
                
def client_sender():
    global sequence
    sequence = 1
    while True:
        type = input("Select Message Type: ")
        if type == 'm':
            message = input("Enter your message: ")

            packet = handlers.create_message(magic, client_id, sequence, 0, 1, 0, message)
            dec_pack = handlers.decode_packet(packet)
            sent_packets[dec_pack.pack_num] = dec_pack

            client_socket.sendto(packet, server_addr)
            print("Sent message to Server: {}".format(message))
            start_timeout(dec_pack.pack_num)

        elif type == 'v':
            question = input("Enter your question: ")

            packet = handlers.create_question(magic, client_id, sequence, 0, 1, 0, 0, question)
            dec_pack = handlers.decode_packet(packet)
            sent_packets[dec_pack.pack_num] = dec_pack
            
            client_socket.sendto(packet, server_addr)
            print("Sent Question to Server: {}". format(question))
            start_timeout(dec_pack.pack_num)

        sequence= sequence + 1

def main():

    startup_sequence()

    send_thread = threading.Thread(target=client_sender, )
    send_thread.start()

    listen_thread = threading.Thread(target=client_listener, )
    listen_thread.start()

if __name__ == "__main__":
    main()


def client_processor(received):
    global connected
    global sequence
    
    # Data
    if (received.type == 0):
        # Deal with differnt data responses from the server.
        if received.packet_id == 1:
            recv_packets[received.pack_num] = received
            print(f"Received Hello Response Packet from server: {received.pack_num}")
            handlers.send_ack(client_socket, server_addr, received, client_id) 
            connected = True

        elif received.packet_id == 3:
            recv_packets[received.pack_num] = received
            print(f"Received Question from server: {received.question}")
            handlers.send_ack(client_socket, server_addr, received, client_id)
            answer = voting.get_answer(received.question)
            if 5 in features:
                answer = not answer
            my_answer = handlers.create_vote_response(magic, client_id, sequence, 0, 1, 0, received.vote_id, answer)
            client_socket.sendto(my_answer, server_addr)
            sequence = sequence + 1
            print(f"Sent Response to Poll {received.vote_id} : ")
            
        elif received.packet_id == 5:
            recv_packets[received.pack_num] = received
            print(f"Received Vote Result From Server:\nVote ID {received.vote_id}\nResult {received.result}")
            handlers.send_ack(client_socket, server_addr, received, client_id)

        elif received.packet_id == 6:
            recv_packets[received.pack_num] = received
            print(f"Received Message From Server: {received.message}")
            handlers.send_ack(client_socket, server_addr, received, client_id)

    # ACK
    elif (received.type == 1):
        ack_packets[received.pack_num] = received
        print(f"From Server: ACK {received.pack_num}")

    # NACK
    elif received.type == 2:
        print(f"From Server: NACK {received.pack_num}")
