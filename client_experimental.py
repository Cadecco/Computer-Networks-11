import array
import socket
import struct

def chksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff


class TCPPacket:
    def __init__(self,
                 src_host:  str,
                 src_port:  int,
                 dst_host:  str,
                 dst_port:  int,
                 flags:     int = 0):
        self.src_host = src_host
        self.src_port = src_port
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.flags = flags

    def build(self) -> bytes:
        packet = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            0,              # Sequence Number
            0,              # Acknoledgement Number
            5 << 4,         # Data Offset
            self.flags,     # Flags
            8192,           # Window
            0,              # Checksum (initial value)
            0               # Urgent pointer
        )

        pseudo_hdr = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_host),    # Source Address
            socket.inet_aton(self.dst_host),    # Destination Address
            socket.IPPROTO_TCP,                 # PTCL
            len(packet)                         # TCP Length
        )

        checksum = chksum(pseudo_hdr + packet)

        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        return packet

if __name__ == "__main__":
    server_ip = "172.20.10.7"
    port = 61009

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.connect((server_ip, port))

while True:

    # Prompt for Sending string to the server.
    message = input("Enter your protocol number or a message: ")

    if  int(message):
        pak = TCPPacket(
        '192.168.1.42',
        20,
        server_ip,
        666,
        0b000101001  # Merry Christmas!
        )  

        server.sendto(pak.build(), (server_ip, 0))

    else:
        server.send(bytes(message, "utf-8"))

    if message == "END":
        break
