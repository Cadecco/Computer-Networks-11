import socket
import random
import zlib
import struct

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

def get_checksum(data):
    checksum = zlib.crc32(data)
    return checksum

def create_packet(data):
    packet = data.encode()
    checksum = get_checksum(packet)

    # Creating the UDP header with 4 fields all of 4 bytes long.
    # One 'I' size is 4 bytes, so 4 items x 4 = 16 bytes of header.
    header = struct.pack("!IIIIHH", magic, checksum, id, seq_num, final, type)

    body = struct.pack()

    udp_packet = header + packet
    return udp_packet


def main():

    server_addr = (host, port)

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        message = input("Enter Message: ")

        packet = create_packet(message)

        client_socket.sendto(packet, server_addr)

        print("Sent message to server: {}".format(message))

        received, addr = client_socket.recvfrom(1024)
        print(f"{received.decode()}")

        
if __name__ == "__main__":
    main()
