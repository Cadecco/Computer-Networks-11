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

magic = 17109271
chats = {}

def get_checksum(data):
    checksum = zlib.crc32(data)
    return checksum

def corruption_check(packet):
    correct_checksum = packet.checksum
    checksum = get_checksum(packet.data)
    corrupted = correct_checksum != checksum
    return corrupted

def client_kill(addr, id):
    chats.pop(id)
    print(f"Client {id} Terminated")

class udp_packet:
    def __init__(self, magic, checksum, id, seq_num, final, type, data):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type
        self.data = data


def send_ack(server_socket, addr, packet, id):
    ack_packet = create_packet(packet.magic, id, packet.seq_num, packet.final, 1, 'ACK')
    server_socket.sendto(ack_packet, addr)
    #print(f"{len(ack_packet)}")
    print(f"ACK Sent")

def send_nack(server_socket, addr, packet, id):
    nack_packet = create_packet(packet.magic, id, packet.seq_num, packet.final, 2, 'NACK')
    server_socket.sendto(nack_packet, addr)
    print(f"NACK Sent")

def send_list(server_socket, addr, packet, id):
    list_packet = create_packet(packet.magic, id, packet.seq_num, packet.final, 2, )
    server_socket.sendto(list_packet, addr)
    print(f"List Sent")

def vote_packet(server_socket, addr):
    vote = create_packet(magic, 1, 1, 1, 0, "Hello")
    server_socket.sendto(vote, addr)
    #print(f"Vote Broadcast")

def answer_vote(socket, addr, received):
    parts = received.split('=')
    if len(parts) != 2:
        print("Invalid equation format.")
        return

    # Evaluate the LHS and RHS expressions
    print("evaluating")
    lhs = eval(parts[0].strip())
    rhs = eval(parts[1].strip())

    # Check if the LHS equals the RHS
    check = lhs == rhs
    print(check)
    return check



def resend(socket, addr, sent, received):
    packet = sent.get(received.seq_num)
    send_packet = encode_packet(packet)
    socket.sendto(send_packet, addr)
    print(f"\nResent to {addr}: {packet.data.decode()} with Sequence No. {packet.seq_num}")


def create_packet(magic, id, seq_num, final, type, data):
    body = data.encode()
    checksum = get_checksum(body)

    # Creating the UDP header with 4 fields all of 4 bytes long.
    # One 'I' size is 4 bytes, so 4 items x 4  + 2 x 2 bytes = 20 bytes of header.
    header = struct.pack("!IIIIHH", magic, checksum, id, seq_num, final, type)

    udp_packet = header + body
    return udp_packet

def encode_packet(packet):
    data = packet.data.decode()
    new_packet = create_packet(packet.magic, packet.client_id, packet.seq_num, packet.final, packet.type, data)
    return new_packet

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


def handle_request(server_socket, addr, packet):
    if packet.data == "List":
        send_list(addr, packet)
    
