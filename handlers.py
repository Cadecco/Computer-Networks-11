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
    checksum = get_checksum()
    corrupted = correct_checksum != checksum
    return corrupted

def client_kill(addr, id):
    chats.pop(id)
    print(f"Client {id} Terminated")

#0
class hello_packet:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, version, num_features, features):
        # TXP Protocol
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        # Consensus Protocol
        self.packet_id = packet_id
        self.version = version
        self.num_features = num_features
        self.feeatures = features

#1
class hello_response:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, version, num_features, features):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.version = version
        self.num_features = num_features
        self.feeatures = features
#2
class client_question:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, vote_id, question_length, question):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.question_length = question_length
        self.question = question

#3
class question_broadcast:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, vote_id, question_length, question):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.question_length = question_length
        self.question = question

#4
class vote_response:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, vote_id, response):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.response = response

#5
class result_broadcast:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, vote_id, result):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.result = result

#6
class message_packet:
    def __init__(self, magic, checksum, id, seq_num, final, type, packet_id, vote_id, result):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.result = result


def send_ack(server_socket, addr, packet, id):
    ack_packet = create_ACK_NACK(packet.magic, id, packet.seq_num, packet.final, 1)
    server_socket.sendto(ack_packet, addr)
    #print(f"{len(ack_packet)}")
    print(f"ACK {packet.seq_num} Sent")

def send_nack(server_socket, addr, packet, id):
    nack_packet = create_ACK_NACK(packet.magic, id, packet.seq_num, packet.final, 2)
    server_socket.sendto(nack_packet, addr)
    print(f"NACK Sent")

def send_list(server_socket, addr, packet, id):
    list_packet = create_packet(packet.magic, id, packet.seq_num, packet.final, 2, )
    server_socket.sendto(list_packet, addr)
    print(f"List Sent")


def resend(socket, addr, sent, received):
    packet = sent.get(received.seq_num)
    send_packet = encode_packet(packet)
    socket.sendto(send_packet, addr)
    print(f"\nResent to {addr}: {packet.data.decode()} with Sequence No. {packet.seq_num}")

#----------------------------------------------------------------------

#0
def create_hello_packet(magic, id, seq_num, final, type, version, num_features, features):
    num_features = len(features)
    pip_header = struct.pack("!H", '0')
    pip_body = struct.pack("!IHH", version, num_features) + features.encode('ascii')

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#1
def create_hello_response(magic, id, seq_num, final, type, version, num_features, features):
    num_features = len(features)
    pip_header = struct.pack("!H", '1')
    pip_body = struct.pack("!IHH", version, num_features) + features.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#2
def create_question(magic, id, seq_num, final, type, vote_id, question):
    pip_header = struct.pack("!H", '2')
    question_length = len(question)
    en_question = question.encode()
    pip_body = struct.pack("!II", vote_id, question_length) + en_question.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#3
def create_question_broadcast(magic, id, seq_num, final, type, vote_id, question):
    pip_header = struct.pack("!H", '3')
    question_length = len(question)
    en_question = question.encode()
    pip_body = struct.pack("!II", vote_id, question_length) + en_question.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#4
def create_vote_response(magic, id, seq_num, final, type, vote_id, response):
    pip_header = struct.pack("!H", '4')
    pip_body = struct.pack("!IH", vote_id, response)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#5
def create_result_broadcast(magic, id, seq_num, final, type, vote_id, result):
    pip_header = struct.pack("!H", '5')
    pip_body = struct.pack("!IH", vote_id, result)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet

#6
def create_message(magic, id, seq_num, final, type, message):
    pip_header = struct.pack("!H", '6')
    pip_body = message.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, seq_num, final, type, pip)
    return packet


#----------------------------------------------------------------------

def create_ACK_NACK(magic, id, seq_num, final, type):
    no_checksum_head = struct.pack("!IIHH", id, seq_num, final, type)
    checksum = get_checksum(no_checksum_head)

    header = struct.pack("!IIIIHH", magic, checksum, id, seq_num, final, type)
    return header

def combine_packet(magic, id, seq_num, final, type, pip):

    # Get the checksum on everything after the magic and checksum.
    no_checksum_head = struct.pack("!IIHH", id, seq_num, final, type)
    no_checksum = no_checksum_head + pip

    checksum = get_checksum(no_checksum)
    # Creating the UDP header with 4 fields all of 4 bytes long.
    # One 'I' size is 4 bytes, so 4 items x 4  + 2 x 2 bytes = 20 bytes of header.
    header = struct.pack("!IIIIHH", magic, checksum, id, seq_num, final, type)

    udp_packet = header + pip
    return udp_packet

def encode_packet(packet):
    if packet.
    data = packet.data.decode()
    new_packet = create_packet(packet.magic, packet.client_id, packet.seq_num, packet.final, packet.type, data)
    return new_packet

def decode_packet(packet):
    # Extract everything up to and including the 16th byte as header.
    header = packet[:20]
    # Everything After this is the data that was sent.
    pip_header = packet[20:22]
    pip_header = struct.unpack("!H", pip_header)
    body = packet[22:]
    header = struct.unpack("!IIIIHH", header)
    # The third entry in the header is the checksum.
    magic = header[0]
    checksum = header[1]
    id = header[2]
    seq_num = header[3]
    final = header[4]
    type = header[5]

    if pip_header == 0:
        body = struct.unpack("!IH", body)
        version = body[0]
        num_features = body[1]
        features = packet[28:]
        new_packet = hello_packet(magic, checksum, id, seq_num, final, type, pip_header, version, num_features, features)
    elif pip_header == 1:
        body = struct.unpack("!IH", body)
        version = body[0]
        num_features == body[1]
        features = packet[28:]
        new_packet = hello_response(magic, checksum, id, seq_num, final, type, pip_header, version, num_features, features)
    elif pip_header == 2:
        body = struct.unpack("!II", body)
        vote_id = body[0]
        question_length = body[1]
        question = packet[30:]
        new_packet = client_question(magic, checksum, id, seq_num, final, type, pip_header, vote_id, question_length, question)
    elif pip_header == 3:
        body = struct.unpack("!II", body)
        vote_id = body[0]
        question_length = body[1]
        question = packet[30:]
        new_packet = question_broadcast(magic, checksum, id, seq_num, final, type, pip_header, vote_id, question_length, question)
    elif pip_header == 4:
        body = struct.unpack("!IH", body)
        vote_id = body[0]
        response = body[1]
        new_packet = vote_response(magic, checksum, id, seq_num, final, type, pip_header, vote_id, response)
    elif pip_header == 5:
        body =struct.unpack("!IH", body)
        vote_id = body[0]
        result = body[1]
        new_packet = result_broadcast(magic, checksum, id, seq_num, final, type, pip_header, vote_id, result)
    elif pip_header == 6:
        message = packet[22:]
        new_packet = message_packet(magic, checksum, id, seq_num, final, type, pip_header, message)

    return new_packet


def handle_request(server_socket, addr, packet):
    if packet.data == "List":
        send_list(addr, packet)
    