import socket
import utils
import packet
import sender
import receiver

from sock_utils import create_receiver_sock, wait_synack, send_syn, wait_syn, wait_confirm, send_confirmation, wait_close

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
    conn.source_ip = localhost
    conn.source_port = localport

    return conn


def accept(conn) -> Conn:
    print('WAITING FOR SYN...')
    synack_pack = wait_syn(conn)
    print('SYN RECEIVED')
    print('SYNACK SENT...')
    print('WAITING CONFIRMATION...')
    conf_pack = wait_confirm(conn, synack_pack)
    print('CONFIRMATION RECEIVED')
    conn.source_ip = conf_pack.dest_ip
    conn.source_port = conf_pack.dest_port
    conn.dest_ip = conf_pack.source_ip
    conn.dest_port = conf_pack.source_port
    conn.seq_num = conf_pack.ack
    conn.ack = conf_pack.seq_num

    return conn

def dial(address) -> Conn:
    print('DIALING...')
    host, port = '10.0.0.1', 8000
    conn = Conn()
    conn.socket.bind((host, port))
    conn.source_ip = conn.host = host
    conn.source_port = conn.port = port


    syn_pack = send_syn(conn, address)
    conn.dest_ip = syn_pack.dest_ip
    conn.dest_port = syn_pack.dest_port
    print('WAITING FOR SYNACK...')
    synack_pack = wait_synack(conn, syn_pack)
    print('SYNACK RECEIVED')
    print('SENDING CONFIRMATION...')
    conf_pack = send_confirmation(conn, synack_pack)
    print('CONFIRMATION SENT')
    conn.seq_num = conf_pack.ack + 1
    conn.ack = conf_pack.seq_num

    return conn

def send(conn: Conn, data: bytes) -> int:
    sender.send(conn, data)

def recv(conn: Conn, length: int) -> bytes:
    packs = receiver.receive(conn, length)
    return packs


def close(conn: Conn):
    close_packet = packet.create_close_packet(conn)
    flags = packet.create_flags(False, False, True)
    close_pack = wait_close(conn, close_packet)
    conn.sock = None
    print('CONNECTION CLOSED')