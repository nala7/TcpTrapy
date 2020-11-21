import array
import socket
from struct import pack, unpack


def create_flags(ack = False, syn = False):
    flags = 0

    flags += 0b00010000 if ack else 0b00000000
    flags += 0b00000010 if ack else 0b00000000

    return flags

def create_syn_packet(source_port, destination_port, sequence_number, source_ip, dest_ip):
    flags = create_flags(ack=False, syn=True)
    packet = Packet(source_port, destination_port, 0, 0, source_ip, dest_ip, flags)
    packet = packet.pack
    return packet

def create_ack_packet(source_port, dest_port, sequence_number, source_ip, dest_ip):
    flags = create_flags(ack=True)
    packet = Packet(source_port, dest_port, sequence_number, 0, source_ip, dest_ip, flags)
    packet = packet.pack
    return packet


class Packet:
    def __init__(self,
                 source_port=0,
                 destination_port=0,
                 sequence_number=0,
                 ack=0,
                 source_ip='',
                 dest_ip='',
                 flags=0,
                 data: bytes = b''):
        self.source_port = source_port 
        self.dest_port = destination_port
        self.seq_num = sequence_number
        self.ack = ack
        self.data_len = len(data)
        self.data = data
        if not len(self.data) % 2 == 0:
            self.data += b'0'
        self.checksum = 0
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.flags = flags

    def build_ip_header(self):
        ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
        ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
        ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum
        ip_header += socket.inet_aton(self.source_ip)  # Source Address
        ip_header += socket.inet_aton(self.dest_ip)  # Destination Address

        return ip_header

    def build_tcp_header(self):
        tcp_header = pack('!HH', self.source_port,
                          self.dest_port)  # Source Port | Destination Port
        tcp_header += pack('!L', self.seq_num)  # Sequence Number
        tcp_header += pack('!L', self.ack)  # Acknowledgement Number
        tcp_header += pack('!bb', self.flags, 0)  # Flags | Unused
        tcp_header += pack('!H', self.data_len)  # Data Lenght

        self.checksum = self.get_checksum(tcp_header + self.data)
        tcp_header += pack('!H', self.checksum)  # Checksum

    def get_checksum(self, packet: bytes) -> int:
        if len(packet) % 2 != 0:
            packet += b'\0'

        res = sum(array.array("H", packet))
        res = (res >> 16) + (res & 0xffff)
        res += res >> 16

        return (~res) & 0xffff

    def pack(self, packet_flag = ''):
        return self.build_ip_header() + self.build_tcp_header() + self.data


    def unpack(self, packed_data):
        ipHeader = packed_data[0:20]
        tcpHeader = packed_data[20:38]
        body = packed_data[38:]

        self.source_ip = socket.inet_ntoa(ipHeader[12:16])
        self.dest_ip = socket.inet_ntoa(ipHeader[16:20])
        self.source_port, self.dest_port, self.seq_num, self.ack, self.flags, _, self.data_len, self.checksum = unpack("!HHLLbbHH", tcpHeader)
        self.data = body

    def is_ack(self):
        is_ack = ((self.flags >> 4) & 1) == 1
        return (is_ack)

    def is_syn(self):
        is_syn = ((self.flags >> 1) & 1) == 1
        return(is_syn)
