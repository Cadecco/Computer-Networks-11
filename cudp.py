import socket
import random
import zlib
import struct
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


def main():

    server_addr = (host, port)

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        message = input("Enter Message: ")
        #message = "Hello"

        packet = handlers.create_packet(magic, id, seq_num, final, type, message)

        client_socket.sendto(packet, server_addr)

        print("Sent message to server: {}".format(message))


        rec_pack, addr = client_socket.recvfrom(1024)
        print(f"{len(rec_pack)}")
        received = handlers.decode_packet(rec_pack)
        print(f"From Server: {received.data.decode()}")

        # Delay For testing.
        #time.sleep(1)
        
if __name__ == "__main__":
    main()
