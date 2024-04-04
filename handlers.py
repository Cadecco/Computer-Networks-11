import struct
import zlib
import uuid # For generating Vote IDs

magic = 0x01051117
chats = {}

def get_checksum(data):
    checksum = zlib.crc32(data)
    return checksum

def corruption_check(packet):
    correct_checksum = packet.checksum
    enc_pack = encode_packet(packet)
    checksum = get_checksum(enc_pack[8:])
    corrupted = correct_checksum != checksum
    return corrupted

def client_kill(addr, id):
    chats.pop(id)
    print(f"Client {id} Terminated")

class ACK:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 1

class NACK:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 2

class SYN:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 3

class SYN_ACK:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 4

class PING_REQ:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 0xFFFE

class PING_RES:
    def __init__(self, magic, checksum, client_id, pack_num, seq_num, final):
        self.magic = magic
        self.checksum = checksum
        self.client_id = client_id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = 0xFFFF


#0
class hello_packet:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, version, num_features, features):
        # TXP Protocol
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        # Consensus Protocol
        self.packet_id = packet_id
        self.version = version
        self.num_features = num_features
        self.features = features

#1
class hello_response:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, version, num_features, features):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.version = version
        self.num_features = num_features
        self.features = features
#2
class client_question:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, vote_id, question_length, question):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.question_length = question_length
        self.question = question

#3
class question_broadcast:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, vote_id, question_length, question):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.question_length = question_length
        self.question = question

#4
class vote_response:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, vote_id, response):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.response = response

#5
class result_broadcast:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, vote_id, result):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.vote_id = vote_id
        self.result = result

#6
class message_packet:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, message):
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        self.packet_id = packet_id
        self.message = message

class client_packet:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id, client, num_features, features):
        # TXP Protocol
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        # Consensus Protocol
        self.packet_id = packet_id
        self.version == client
        self.num_features = num_features
        self.features = features

class unknown:
    def __init__(self, magic, checksum, id, pack_num, seq_num, final, type, packet_id):
        # TXP Protocol
        self.magic = magic
        self.checksum = checksum
        self.client_id = id
        self.pack_num = pack_num
        self.seq_num = seq_num
        self.final = final
        self.type = type

        # Consensus Protocol
        self.packet_id = packet_id

def send_ack(socket, addr, packet, id):
    ack_packet = create_ACK_NACK(packet.magic, id, packet.pack_num, packet.seq_num, packet.final, 1)
    socket.sendto(ack_packet, addr)
    print(f"ACK {packet.pack_num} Sent to {addr}")

def send_nack(socket, addr, packet, id):
    nack_packet = create_ACK_NACK(packet.magic, id, packet.pack_num, packet.seq_num, packet.final, 2)
    socket.sendto(nack_packet, addr)
    print(f"NACK {packet.pack_num} Sent")


def resend(socket, addr, sent, received):
    packet = sent.get(received.seq_num)
    send_packet = encode_packet(packet)
    socket.sendto(send_packet, addr)
    if packet.packet_id == 6:
        message = packet.message
    elif packet.packet_id == 2:
        message = packet.question
    elif packet.packet_id == 0:
        message = "Hello Packet"
    elif packet.packet_id == 1:
        message = "Hello Response"
    elif packet.packet_id == 3:
        message = packet.question
    elif packet.packet_id == 4:
        message = packet.response
    elif packet.packet_id == 5:
        message = packet.result
    print(f"\nResent to {addr}: {message} with Sequence No. {packet.seq_num}")

#----------------------------------------------------------------------

#0
def create_hello_packet(magic, id, pack_num, seq_num, final, type, version, num_features, features):
    num_features = len(features)
    pip_header = struct.pack("!H", 0)
    pip_body = struct.pack("!IH", version, num_features)
    for x in range(num_features):
        feature = features[x]
        pip_body = pip_body + struct.pack("!H", feature)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#1
def create_hello_response(magic, id, pack_num, seq_num, final, type, version, num_features, features):
    num_features = len(features)
    pip_header = struct.pack("!H", 1)
    pip_body = struct.pack("!IH", version, num_features)
    for x in range(num_features):
        feature = features[x]
        pip_body = pip_body + struct.pack("!H", feature)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#2
def create_question(magic, id, pack_num, seq_num, final, type, vote_id, question):
    pip_header = struct.pack("!H", 2)
    question_length = len(question)
    if vote_id == 0:
        vote_id = uuid.uuid4()
    vote_id = vote_id.bytes
    pip_body = vote_id + struct.pack("!I", question_length)  + question.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#3
def create_question_broadcast(magic, id, pack_num, seq_num, final, type, vote_id, question):
    pip_header = struct.pack("!H", 3)
    question_length = len(question)
    if vote_id == 0:
        vote_id = uuid.uuid4()
    vote_id = vote_id.bytes
    pip_body = vote_id + struct.pack("!I", question_length) + question.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#4
def create_vote_response(magic, id, pack_num, seq_num, final, type, vote_id, response):
    pip_header = struct.pack("!H", 4)
    vote_id = vote_id.bytes
    pip_body = vote_id + struct.pack("!H", response)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#5
def create_result_broadcast(magic, id, pack_num, seq_num, final, type, vote_id, result):
    pip_header = struct.pack("!H", 5)
    vote_id = vote_id.bytes
    pip_body = vote_id + struct.pack("!H", result)

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet

#6
def create_message(magic, id, pack_num, seq_num, final, type, message):
    pip_header = struct.pack("!H", 6)
    pip_body = message.encode()

    pip = pip_header + pip_body
    packet = combine_packet(magic, id, pack_num, seq_num, final, type, pip)
    return packet


#----------------------------------------------------------------------

def create_ACK_NACK(magic, id, pack_num, seq_num, final, type):
    no_checksum_head = struct.pack("!IIIHH", id, pack_num, seq_num, final, type)
    checksum = get_checksum(no_checksum_head)

    header = struct.pack("!IIIIIHH", magic, checksum, id, pack_num, seq_num, final, type)
    return header

def combine_packet(magic, id, pack_num, seq_num, final, type, pip):

    # Get the checksum on everything after the magic and checksum.
    no_checksum_head = struct.pack("!IIIHH", id, pack_num, seq_num, final, type)
    no_checksum = no_checksum_head + pip

    checksum = get_checksum(no_checksum)
    # Creating the UDP header with 4 fields all of 4 bytes long.
    # One 'I' size is 4 bytes, so 4 items x 4  + 2 x 2 bytes = 20 bytes of header.
    header = struct.pack("!IIIIIHH", magic, checksum, id, pack_num, seq_num, final, type)

    udp_packet = header + pip
    return udp_packet

def encode_packet(p):
    if p.type == 1:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 1)
        return packet
    elif p.type == 2:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 2)
    elif p.type == 3:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 3)
    elif p.type == 4:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 4)
    elif p.type == 0xFFFE:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 0xFFFE)
    elif p.type == 0xFFFF:
        packet = create_ACK_NACK(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, 0xFFFF)
    elif p.type == 0:
        if p.packet_id == 0:
            packet = create_hello_packet(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type,  p.version, p.num_features, p.features)
            return packet
        elif p.packet_id == 1:
            packet = create_hello_response(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.version, p.num_features, p.features)
            return packet
        elif p.packet_id == 2:
            packet = create_question(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.vote_id, p.question)
            return packet
        elif p.packet_id == 3:
            packet = create_question_broadcast(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.vote_id, p.question)
            return packet
        elif p.packet_id == 4:
            packet = create_vote_response(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.vote_id, p.response)
            return packet
        elif p.packet_id == 5:
            packet = create_result_broadcast(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.vote_id, p.result)
            return packet
        elif p.packet_id == 6:
            packet = create_message(p.magic, p.client_id, p.pack_num, p.seq_num, p.final, p.type, p.message)
            return packet


def decode_packet(packet):
    # Extract everything up to and including the 16th byte as header.
    header = packet[:24]
    # Everything After this is the data that was sent.
    pip_header = packet[24:26]
    if pip_header:
        pip_header = struct.unpack("!H", pip_header)
        pip_header = pip_header[0]
        body = packet[26:]
    header = struct.unpack("!IIIIIHH", header)
    # The third entry in the header is the checksum.
    magic = header[0]
    checksum = header[1]
    id = header[2]
    pack_num = header[3]
    seq_num = header[4]
    final = header[5]
    type = header[6]

    if type == 1:
        new_packet = ACK(magic, checksum, id, pack_num, seq_num, final)
        return new_packet

    elif type == 2:
        new_packet = NACK(magic, checksum, id, pack_num, seq_num, final)
        return new_packet
    
    elif type == 3:
        new_packet = SYN(magic, checksum, id , pack_num, seq_num, final)
        return new_packet
    
    elif type == 4:
        new_packet = SYN_ACK(magic, checksum, id, pack_num, seq_num, final)
        return new_packet
    
    elif type == 0xFFFE:
        new_packet = PING_REQ(magic, checksum, id, pack_num, seq_num, final)
        return new_packet
    
    elif type == 0xFFFF:
        new_packet = PING_RES(magic, checksum, id, pack_num, seq_num, final)
        return new_packet

    elif type == 0:

        if pip_header == 0:
            body = packet[26:32]
            body = struct.unpack("!IH", body)
            version = body[0]
            num_features = body[1]
            features = packet[32:]
            feature_list = []
            feature_list = struct.unpack('!{}H'.format(num_features), features)
            new_packet = hello_packet(magic, checksum, id, pack_num, seq_num, final, type, pip_header, version, num_features, feature_list)
            return new_packet
        elif pip_header == 1:
            body = packet[26:32]
            body = struct.unpack("!IH", body)
            version = body[0]
            num_features = body[1]
            features = packet[32:]
            feature_list = []
            feature_list = struct.unpack("!{}H".format(num_features), features)
            new_packet = hello_response(magic, checksum, id, pack_num, seq_num, final, type, pip_header, version, num_features, features)
            return new_packet
        elif pip_header == 2:
            body = packet[26:46]
            vote_id = body[0:16]
            question_length = body[16:20]
            question = packet[46:]
            question = question.decode()
            vote_id = uuid.UUID(int=int.from_bytes(vote_id, 'big'))
            new_packet = client_question(magic, checksum, id, pack_num, seq_num, final, type, pip_header, vote_id, question_length, question)
            return new_packet
        elif pip_header == 3:
            body = packet[26:46]
            vote_id = body[0:16]
            question_length = body[16:20]
            question = packet[46:]
            question = question.decode()
            vote_id = uuid.UUID(int=int.from_bytes(vote_id, 'big'))
            new_packet = question_broadcast(magic, checksum, id, pack_num, seq_num, final, type, pip_header, vote_id, question_length, question)
            return new_packet
        elif pip_header == 4:
            body = packet[26:42]
            vote_id = body[0:16]
            response = packet[42:]
            response = struct.unpack("!H", response)
            response = response[0]
            vote_id = uuid.UUID(int=int.from_bytes(vote_id, 'big'))
            new_packet = vote_response(magic, checksum, id, pack_num, seq_num, final, type, pip_header, vote_id, response)
            return new_packet
        elif pip_header == 5:
            body = packet[26:42]
            vote_id = body[0:16]
            result = packet[42:]
            result = struct.unpack("!H", result)
            result = result[0]
            vote_id = uuid.UUID(int=int.from_bytes(vote_id, 'big'))
            new_packet = result_broadcast(magic, checksum, id, pack_num, seq_num, final, type, pip_header, vote_id, result)
            return new_packet
        elif pip_header == 6:
            message = packet[26:]
            message = message.decode()
            new_packet = message_packet(magic, checksum, id, pack_num, seq_num, final, type, pip_header, message)
            return new_packet
        elif pip_header == 0x12:
            body = packet[26:34]
            body = struct.unpack("!II", body)
            id = body[0]
            num_features = body[1]
            features = packet[34:]
            feature_list = []
            feature_list = struct.unpack('!{}H'.format(num_features), features)
            new_packet = client_packet(magic, checksum, id, pack_num, seq_num, final, type, pip_header, id, num_features, feature_list)
            return new_packet
            

        else:
            print(f"Unknown Packet Id, Unable to decode")
            new_packet = unknown(magic, checksum, id, seq_num, final, type, pip_header)
            return packet

    else:
        print(f"{packet}")
        print(f"Unkown Packet Type")

