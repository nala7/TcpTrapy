import array
import socket
from struct import pack, unpack


def create_flags(ack = False, syn = False):
    flags = 0

    flags += 0b00010000 if ack else 0b00000000
    flags += 0b00000010 if syn else 0b00000000

    return flags

def create_syn_packet(source_port, dest_port, seq_num, source_ip, dest_ip):
    flags = create_flags(ack=False, syn=True)
    packet = Packet(source_port, dest_port, seq_num, 0, source_ip, dest_ip, flags)
    packet = packet.pack()
    return packet

# def create_ack_packet(source_port, dest_port, seq_num, source_ip, dest_ip):
#     flags = create_flags(ack=True)
#     packet = Packet(source_port, dest_port, seq_num, 0, source_ip, dest_ip, flags)
#     packet = packet.pack()
#     return packet

def create_synack_packet(syn_pack):
    pack = Packet()    
    pack.source_port = syn_pack.dest_port
    pack.dest_port = syn_pack.source_port
    pack.seq_num = syn_pack.ack
    pack.ack = syn_pack.seq_num + 1
    pack.source_ip = syn_pack.dest_ip
    pack.dest_ip = syn_pack.source_ip
    pack.flags = create_flags(ack = True, syn = True)
    pack.data = syn_pack.data
    pack = pack.pack()

    return pack

def create_confirmation_packet(synack_pack):
    pack = Packet()
    pack.source_port = synack_pack.dest_port
    pack.dest_port = synack_pack.source_port
    pack.seq_num = synack_pack.ack
    pack.ack = synack_pack.seq_num + 1
    pack.source_ip = synack_pack.dest_ip
    pack.dest_ip = synack_pack.source_ip
    pack.flags = create_flags()
    pack = pack.pack()

    return pack

def my_unpack(packed_data):
    ipHeader = packed_data[0:20]
    tcpHeader = packed_data[20:38]
    body = packed_data[38:]

    pack = Packet()
    pack.source_ip = socket.inet_ntoa(ipHeader[12:16])
    pack.dest_ip = socket.inet_ntoa(ipHeader[16:20])
    pack.source_port, pack.dest_port, pack.seq_num, pack.ack, pack.flags, _, pack.data_len, pack.checksum = unpack("!HHLLbbHH", tcpHeader)
    pack.data = body
    return pack

def get_checksum(packet: bytes) -> int:
    if len(packet) % 2 != 0:
        packet += b'\0'

    res = sum(array.array("H", packet))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16

    return (~res) & 0xffff

class Packet:
    def __init__(self,
                 source_port=0,
                 dest_port=0,
                 seq_num=0,
                 ack=0,
                 source_ip='',
                 dest_ip='',
                 flags=0,
                 data: bytes = b''):
        self.source_port = source_port 
        self.dest_port = dest_port
        self.seq_num = seq_num
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

        self.checksum = get_checksum(tcp_header + self.data)
        tcp_header += pack('!H', self.checksum)  # Checksum

        return tcp_header

    def pack(self, packet_flag = ''):
        return self.build_ip_header() + self.build_tcp_header() + self.data

    def is_ack(self):
        is_ack = ((self.flags >> 4) & 1) == 1
        return (is_ack)

    def is_syn(self):
        is_syn = ((self.flags >> 1) & 1) == 1
        return(is_syn)
