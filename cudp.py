import socket
import random
import threading
import handlers
import timeout
import voting
#import client_processor

# type PcktHeader struct {
#     Magic        uint32 // 4 bytes
#     Checksum    uint32 // 4 bytes CRC32
#     ConvID        uint32 // 4 bytes
#     SequenceNum    uint32 // 4 bytes
#     Final       uint16 // 2 bytes
#     Type        uint16 // 2 bytes
# }

# // Types
# const (
#     Data            = 0 //
#     ACK          = 1
#     NACK           = 2
# )

# type Pckt struct {
#     Header        PcktHeader // 20 bytes
#     Body           []byte     // N bytes
    
#     // 20 + N <= 256 Bytes
# }

#define MAGIC 17109271

host = '127.0.0.1'
port = 61000
# ID for this client, will not change once generated.
client_id = random.randint(8000, 9000)
magic = 17109271
seq_num = 1
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

def startup_sequence():
    print(f"Enter Features to Add to this Client\n'1' For Simple Math Compute\n'3' For Just Messaging")
    while True:
        feature_input = input()
        if feature_input == '1':
            features.append(feature_input)
            print(f"Feature added")
        elif feature_input == '3':
            features.append(feature_input)
            print(f"Feature Added")
        elif feature_input == "":
            break
        else:
            print(f"Invalid Feature Input, Try Again")

    print(f"Client Initialised With Features: {features}")   

    input(f"Press Any Key to Connect to the Server")

def client_listener():
    while True:
        try:
            rec_pack, addr = client_socket.recvfrom(1024)
            received = handlers.decode_packet(rec_pack)
            client_processor(received)
        except:
            continue

def start_timeout(seq_num):
    timeouts[seq_num] = timeout.timeout(server_addr, seq_num, ack_packets, sent_packets, client_socket)
    #timeouts[seq_num].timeout_loop()
                
def client_sender():
    sequence = 0

    packet = handlers.create_hello_packet(magic, client_id, sequence, True, 0, 1, num_features, features)
    dec_pack = handlers.decode_packet(packet)
    sent_packets[dec_pack.seq_num] = dec_pack
    client_socket.sendto(packet, server_addr)
    print("Sent Hello Message to Server")
    start_timeout(dec_pack.seq_num)

    while True:
        type = input("Select Message Type: ")
        if type == 'm':
            message = input("Enter your message: ")

            packet = handlers.create_message(magic, client_id, sequence, True, 0, message)
            dec_pack = handlers.decode_packet(packet)
            sent_packets[dec_pack.seq_num] = dec_pack

            client_socket.sendto(packet, server_addr)
            print("Sent message to Server: {}".format(message))
            start_timeout(dec_pack.seq_num)

        elif type == 'v':
            question = input("Enter your question: ")

            packet = handlers.create_question(magic, client_id, sequence, True, 0, 0, question)
            dec_pack = handlers.decode_packet(packet)
            sent_packets[dec_pack.seq_num] = dec_pack
            
            client_socket.sendto(packet, server_addr)
            print("Sent Question to Server: {}". format(question))
            start_timeout(dec_pack.seq_num)

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
    
    # Data
    if (received.type == 0):
        # Deal with differnt data responses from the server.
        if received.packet_id == 1:
            recv_packets[received.seq_num] = received
            print(f"Received Hello Packet from server: {received.question}")
            handlers.send_ack(client_socket, server_addr, received, client_id) 

        elif received.packet_id == 3:
            recv_packets[received.seq_num] = received
            print(f"Received Question from server: {received.question}")
            handlers.send_ack(client_socket, server_addr, received, client_id)
            answer = voting.get_answer(received.question)
            my_answer = handlers.create_vote_response(magic, client_id, seq_num, True, 0, received.vote_id, answer)
            client_socket.sendto(my_answer, server_addr)
            print(f"Sent Response to Poll {received.vote_id}")
            
        elif received.packet_id == 5:
            recv_packets[received.seq_num] = received
            print(f"\nReceived Vote Result From Server: Vote ID {received.vote_id}\n Result {received.result}")
            handlers.send_ack(client_socket, server_addr, received, client_id)

        elif received.packet_id == 6:
            recv_packets[received.seq_num] = received
            print(f"Received Message From Server: {received.message}")
            handlers.send_ack(client_socket, server_addr, received, client_id)

    # ACK
    elif (received.type == 1):
        ack_packets[received.seq_num] = received
        print(f"From Server: ACK {received.seq_num}")

    # NACK
    elif received.type == 2:
        print(f"From Server: NACK {received.seq_num}")
