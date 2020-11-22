import socket
import utils
from sock_utils import create_receiver_sock, wait_synack, send_syn, wait_syn, wait_confirm, send_confirmation
import packet


class Conn:
    def __init__(self, sock = None):
        if sock is None:
            sock = create_receiver_sock()
        self.socket = sock


class ConnException(Exception):
    pass


def listen(address: str) -> Conn:
    localhost, localport = utils.parse_address(address)
    conn = Conn()
    conn.socket.bind((localhost, localport))

    return conn


def accept(conn) -> Conn:
    print('WAITING FOR SYN')
    synack_pack = wait_syn(conn)
    print('SYNACK SENT')
    print('WAITING CONFIRMATION')
    wait_confirm(conn, synack_pack)
    print('CONFIRMATION RECEIVED')

    return conn

def dial(address) -> Conn:
    print('DIALING...')
    host, port = '10.0.0.1', 8000
    conn = Conn()
    conn.socket.bind((host, port))
    conn.host = host
    conn.port = port

    syn_pack = send_syn(conn, address)
    print('WAITING FOR SYNACK...')
    synack_pack = wait_synack(conn, syn_pack)
    print('SYNACK RECEIVED')
    print('SENDING CONFIRMATION')
    send_confirmation(synack_pack)

def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass
