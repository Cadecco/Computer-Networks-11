import socket
import random
import threading
import handlers
import timeout
#import functions

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

math_funcs = functions.MathFunctions()

def client_listener():
    counter = 0
    while True:
        try:
            rec_pack, addr = client_socket.recvfrom(1024)
            received = handlers.decode_packet(rec_pack)
            if received.type == 0:
                handlers.send_ack(client_socket, server_addr, received, client_id)
            elif received.type == 1:
                ack_packets[received.seq_num] = received
            elif received.type == 2:
                handlers.resend(client_socket, server_addr, sent_packets, received)
            elif received.type == 4: #4 is the broadcast voting type
                ack_packets[received.seq_num] = received
                print("checking equ")
                check = handlers.answer_vote(client_socket, server_addr, received)
                print("check = " + check)
                if check:
                    packet = handlers.create_packet(magic, client_id, received.sequence, final, 3, "1")
                    dec_pack = handlers.decode_packet(packet)
                    sent_packets[dec_pack.seq_num] = dec_pack
                    print("sent 1")
                else:
                    packet = handlers.create_packet(magic, client_id, received.sequence, final, 3, "0")
                    dec_pack = handlers.decode_packet(packet)
                    sent_packets[dec_pack.seq_num] = dec_pack
                    print("sent 0")

            print(f"\nFrom Server: {received.data.decode()} {received.seq_num}")
        except:
            continue


def start_timeout(seq_num):
    timeouts[seq_num] = timeout.timeout(server_addr, seq_num, ack_packets, sent_packets, client_socket)
    #timeouts[seq_num].timeout_loop()
                
def client_sender():
    sequence = 0
    while True:
        message = input("Enter Message: ")
        #message = "Hello"

        packet = handlers.create_packet(magic, client_id, sequence, final, type, message)
        dec_pack = handlers.decode_packet(packet)
        sent_packets[dec_pack.seq_num] = dec_pack

        client_socket.sendto(packet, server_addr)
        print("Sent message to server: {}".format(message))
        start_timeout(dec_pack.seq_num)

        sequence = sequence + 1

def main():

    send_thread = threading.Thread(target=client_sender, )
    send_thread.start()

    listen_thread = threading.Thread(target=client_listener, )
    listen_thread.start()

if __name__ == "__main__":
    main()
