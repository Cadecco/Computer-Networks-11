import socket
import random
import threading
import handlers
import timeout
import voting
import time
import globals


#define MAGIC 17109271

host = '127.0.0.1'
port = 8080
# ID for this client, will not change once generated.
magic = 0x01051117
sequence = 0
final = 0
type = 0

#host = socket.gethostbyname("33D03-project.college")
server_addr = (host, port)
print(f"{host}")
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

    packet = handlers.create_ACK_NACK(magic, 0, 0, 0, 1, 0xFFFE)
    dec_pack = handlers.decode_packet(packet)
    sent_packets[dec_pack.pack_num] = dec_pack
    #client_socket.sendto(packet, server_addr)
    #print("Sent Ping to Server")
    #start_timeout(dec_pack.pack_num)

    sequence = sequence + 1

def client_listener():
    global sequence
    lock = threading.Lock()
    while True:
        time.sleep(1)
        #print(f"{globals.client_id}")
        if globals.client_id == 0:
                packet = handlers.create_ACK_NACK(magic, 0, 0, 0, 1, 0xFFFE)
                client_socket.sendto(packet, server_addr)
                print(f"Sent Ping to Server")
                time.sleep(1)

        try:
            rec_pack, addr = client_socket.recvfrom(1024)
            #print(f"Received {rec_pack}")
            received = handlers.decode_packet(rec_pack)
            #print(f"Server sent ID {received.client_id}")
            #print(f"{received}")
            with lock:
                client_processor(received)
        except:
            continue

def start_timeout(pack_num):
    timeouts[pack_num] = timeout.timeout(server_addr, pack_num, ack_packets, sent_packets, client_socket)
    #timeouts[pack_num].timeout_loop()
                
def client_sender():

    global sequence
    sequence = 0
    while True:
        type = input("Select Message Type: ")
        if type == 'm':
            if 3 in features:
                message = input("Enter your message: ")

                packet = handlers.create_message(magic, globals.client_id, sequence, 0, 1, 0, message)
                dec_pack = handlers.decode_packet(packet)
                sent_packets[dec_pack.pack_num] = dec_pack

                client_socket.sendto(packet, server_addr)
                print("Sent message to Server: {}".format(message))
                start_timeout(dec_pack.pack_num)
            else:
                print("Messaging Feature not installed on this Client")
                continue

        elif type == 'v':
            if 1 in features:
                question = input("Enter your question: ")

                packet = handlers.create_question(magic, globals.client_id, sequence, 0, 1, 0, 0, question)
                dec_pack = handlers.decode_packet(packet)
                sent_packets[dec_pack.pack_num] = dec_pack
                
                client_socket.sendto(packet, server_addr)
                print("Sent Question to Server: {}". format(question))
                start_timeout(dec_pack.pack_num)
            else:
                print("Voting not installed on this Client")

        elif type == 'h':
            packet = handlers.create_hello_packet(magic, globals.client_id, sequence, 0, 1, 0, 1, num_features, features)
            dec_pack = handlers.decode_packet(packet)
            sent_packets[dec_pack.pack_num] = dec_pack
            
            client_socket.sendto(packet, server_addr)
            print("Sent Hello Packet to Server")
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
            handlers.send_ack(client_socket, server_addr, received, globals.client_id) 
            connected = True

        elif received.packet_id == 3:
            recv_packets[received.pack_num] = received

            print(f"--------------------\n\nReceived Question from server: {received.question}\n{received.vote_id}\n--------------------")

            handlers.send_ack(client_socket, server_addr, received, globals.client_id)
            answer = voting.get_answer(received.question)
            if 5 in features:
                answer = not answer
            my_answer = handlers.create_vote_response(magic, globals.client_id, sequence, 0, 1, 0, received.vote_id, answer)
            client_socket.sendto(my_answer, server_addr)
            sequence = sequence + 1
            print(f"----------\nSent Response to Poll {received.vote_id} : {answer}\n----------")
            #print(f"{my_answer}")
            
        elif received.packet_id == 5:
            recv_packets[received.pack_num] = received
            # if received.result == 1:
            #     message == "True"
            # elif received.result == 0:
            #     message == "False"
            # else:
            #     message = str(received.result)
            if received.result == 1:
                print(f"----------\nReceived Vote Result From Server:\nVote ID {received.vote_id}\nResult True \nCONSENSUS ACHIEVED\n----------\n")
            elif received.result == 0:
                print(f"----------\nReceived Vote Result From Server:\nVote ID {received.vote_id}\nResult False \nCONSENSUS ACHIEVED\n----------\n")
            elif received.result == 2:
                print(f"----------\nReceived Vote Result From Server:\nVote ID {received.vote_id}\nSYNTAX ERROR\n----------")
            handlers.send_ack(client_socket, server_addr, received, globals.client_id)

        elif received.packet_id == 6:
            recv_packets[received.pack_num] = received
            print(f"Received Message From Server: {received.message}")
            handlers.send_ack(client_socket, server_addr, received, globals.client_id)

        elif received.packet_id == 0x12:
                recv_packets[received.pack_num] = received
                print(f"Received Client Packet: {received.client_id}")
                handlers.send_ack(client_socket, server_addr, received, globals.client_id)

        else:
            recv_packets[received.pack_num] = received
            print(f"Received Unkown Type: {received.client_id}")
            handlers.send_ack(client_socket, server_addr, received, globals.client_id)

    elif (received.type == 0xFFFF):
        print(f"Received Ping Response from server")
        # Send Back The SYN
        globals.client_id = received.client_id
        print(f"Server Given ID: {globals.client_id}")
        synack = handlers.create_ACK_NACK(magic, received.client_id, 0, 0, 1, 3)
        client_socket.sendto(synack, server_addr)
        print(f"SYN sent to Server")

    # ACK
    elif (received.type == 1):
        ack_packets[received.pack_num] = received
        print(f"From Server: ACK {received.pack_num}")

    # NACK
    elif received.type == 2:
        print(f"From Server: NACK {received.pack_num}")

    elif received.type == 4:
        print(f"Got SYN ACK From Server, CONNECTED!")
