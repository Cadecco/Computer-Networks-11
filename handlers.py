import struct
import zlib

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

def get_checksum(data):
    checksum = zlib.crc32(data)
    return checksum

class udp_packet:
    def __init__(self, magic, checksum, id, seq_num, final, type, data):
        self.magic = magic
        self.checksum = checksum
        self.id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type
        self.data = data

def resend(server_socket, addr, packet):
    server_socket.sendto(f"Please Resend {packet.seq_num}".encode() , addr)

def send_ack(server_socket, addr, packet):
    ack_packet = create_packet(packet.magic, packet.id, packet.seq_num, packet.final, 1, None)
    server_socket.sendto(ack_packet, addr)
    print(f"{len(ack_packet)}")
    print(f"Ack Sent")

def send_nack(server_socket, addr, packet):
    nack_packet = create_packet(packet.magic, packet.id, packet.seq_num, packet.final, 2, None)
    server_socket.sendto(nack_packet, addr)

def create_packet(magic, id, seq_num, final, type, data):
    body = data.encode()
    checksum = get_checksum(body)

    # Creating the UDP header with 4 fields all of 4 bytes long.
    # One 'I' size is 4 bytes, so 4 items x 4 = 16 bytes of header.
    header = struct.pack("!IIIIHH", magic, checksum, id, seq_num, final, type)

    udp_packet = header + body
    return udp_packet

def decode_packet(packet):
    # Extract everything up to and including the 16th byte as header.
    header = packet[:20]
    # Everything After this is the data that was sent.
    data = packet[20:]
    header = struct.unpack("!IIIIHH", header)
    # The third entry in the header is the checksum.
    magic = header[0]
    checksum = header[1]
    id = header[2]
    seq_num = header[3]
    final = header[4]
    type = header[5]

    new_packet = udp_packet(magic, checksum, id, seq_num, final, type, data)
    return new_packet
