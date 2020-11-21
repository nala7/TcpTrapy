import socket
import utils
import sock_utils
import packet
from random import randint


class Conn:
    def _init_(self, localhost, localport):
        self.sock = sock_utils.create_sender_sock()
        self.localhost = localhost
        self.localport = localport
        self.sock.bind((localhost, localport))


class ConnException(Exception):
    pass


def listen(address: str) -> Conn:
    pass


def accept(conn) -> Conn:
    
    
    pass


def dial(address) -> Conn:
    host, port = '10.0.0.01', 8080
    conn = Conn(host, port)
    
    seq_num = randint(0, 99)

    dest_host, dest_port = utils.parse_address(address)
    
    pack = packet.create_syn_packet(port, dest_port, seq_num, host, dest_host)

    conn.sock.sendto(pack, (dest_host, dest_port))





def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass
