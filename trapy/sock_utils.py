import socket
from timer import Timer
import packet
import threading
import utils
from random import randint
import time

sender_sock_protocol = socket.SOCK_RAW 
receiver_sock_protocol = socket.IPPROTO_TCP
TIMEOUT_INTERVAL = 0.05
SLEEP_INTERVAL = 0.1

mutex = threading.Lock()
send_timer = Timer(TIMEOUT_INTERVAL)

def create_sender_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, sender_sock_protocol)
    except socket.error:
        print('Sender raw socket could not be created')
    return sock

def create_receiver_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, receiver_sock_protocol)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except socket.error:
        print('Receiver raw socket could not be created')
    return sock

def send_syn(conn, address):
    seq_num = randint(1, 99)
    conn.dest_host, conn.dest_port = utils.parse_address(address)
    pack = packet.create_syn_packet(conn.port, conn.dest_port, seq_num, conn.host, conn.dest_host)
    conn.socket.sendto(pack, (conn.dest_host, conn.dest_port))
    pack = packet.my_unpack(pack)

    return pack

def wait_syn(conn):
    while True:
        syn_pack, _ = conn.socket.recvfrom(1024)
        # if packet.get_checksum(syn_pack) is not  0xffff:
        #     continue
        syn_pack = packet.my_unpack(syn_pack)
        print(syn_pack.source_ip)
        conn.dest_host = syn_pack.source_ip
        conn.dest_port = syn_pack.source_port
        if syn_pack.is_syn():
            synack_pack = packet.create_synack_packet(syn_pack)
            conn.socket.sendto(synack_pack, (syn_pack.source_ip, syn_pack.source_port))
            return synack_pack

def wait_confirm(conn, synack_pack):
    global mutex
    global send_timer
    
    timer = Timer(TIMEOUT_INTERVAL) 
    threading.Thread(target=timer_send_pack, args=(conn, synack_pack, timer)).start()
    send_timer.start()

    while True:
        conf_pack, _ = conn.socket.recvfrom(1024)
        conf_pack = packet.my_unpack(conf_pack)

        if conf_pack.is_ack() and conf_pack.seq_num == synack_pack.ack:
            print('CONFIRMATION RECEIVED')
            mutex.acquire()
            send_timer.stop()
            mutex.release()
            return conf_pack

def wait_synack(conn, syn_pack):
    global mutex
    global send_timer
    
    timer = Timer(TIMEOUT_INTERVAL) 
    print(syn_pack)
    flags = packet.create_flags(False, True)
    syn_packed = syn_pack.pack(flags)
    threading.Thread(target=timer_send_pack, args=(conn, syn_packed, timer)).start()
    send_timer.start()

    while True:
        print('waiting synack')
        synack_pack, _ = conn.socket.recvfrom(1024)
        print(synack_pack)
        # if packet.get_checksum(synack_pack) is not 0xffff:
        #     continue
        synack_pack = packet.my_unpack(synack_pack)
        print(synack_pack.is_syn())
        print(synack_pack.is_ack())
        print(synack_pack.seq_num == syn_pack.ack)
        print(synack_pack.source_ip == syn_pack.dest_ip)
        print(synack_pack.source_port == syn_pack.dest_port)

        if synack_pack.is_syn() and synack_pack.is_ack() and synack_pack.seq_num == syn_pack.ack and synack_pack.source_ip == syn_pack.dest_ip and synack_pack.source_port == syn_pack.dest_port:
            print('SYNACK RECEIVED')
            mutex.acquire()
            send_timer.stop()
            mutex.release()
            return synack_pack

def send_confirmation(conn, synack_pack):
    conf_pack = packet.create_confirmation_packet(synack_pack)
    conn.socket.sendto(conf_pack, (conn.dest_host, conn.dest_port))


def timer_send_pack(conn, pack, timer):
    global mutex
    global send_timer

    while True:
        if not send_timer.running():
            break
        if send_timer.timeout():
            mutex.acquire()
            conn.socket.sendto(pack, (conn.dest_host, conn.dest_port))
            send_timer.start()
            mutex.release()
        time.sleep(SLEEP_INTERVAL)
