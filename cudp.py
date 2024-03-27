import socket
import random
import threading
import time
import handlers

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
id = random.randint(8000, 9000)
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

class timeout:
    def __init__(self, seq_num):
        self.seq_num = seq_num
        self.exceptions = 0

        #self.lock = threading.Lock()
        #self.timeout_thread = threading.Thread(target=self.timeout_loop, )
        #self.timeout_thread.start()

        self.timer = 0

    def timeout_loop(self):
        self.timer = time.time() + 3
        #with self.lock:

        while time.time() < self.timer:
                received = ack_packets.get(self.seq_num)
                #print(f"{received}")
                if received and received.type == 1:
                    return
                    
        resend(sent_packets[self.seq_num])

def client_listener():
    counter = 0
    while True:
        try:
            rec_pack, addr = client_socket.recvfrom(1024)
            received = handlers.decode_packet(rec_pack)
            ack_packets[received.seq_num] = received
            print(f"\nFrom Server: {received.data.decode()} {received.seq_num}")
        except:
            continue


def resend(received):
    packet = sent_packets.get(received.seq_num)
    send_packet = handlers.encode_packet(packet)
    client_socket.sendto(send_packet, server_addr)
    print(f"\nResent to server: {packet.data.decode()} with Sequence No. {packet.seq_num}")

def start_timeout(seq_num):
    timeouts[seq_num] = timeout(seq_num)
    timeouts[seq_num].timeout_loop()
                
def client_sender():
    sequence = 0
    while True:
        message = input("Enter Message: ")
        #message = "Hello"

        packet = handlers.create_packet(magic, id, sequence, final, type, message)
        dec_pack = handlers.decode_packet(packet)
        sent_packets[dec_pack.seq_num] = dec_pack

        client_socket.sendto(packet, server_addr)
        start_timeout(dec_pack.seq_num)
        print("Sent message to server: {}".format(message))

        sequence = sequence + 1

def main():

    send_thread = threading.Thread(target=client_sender, )
    send_thread.start()
    
    listen_thread = threading.Thread(target=client_listener, )
    listen_thread.start()

if __name__ == "__main__":
    main()
