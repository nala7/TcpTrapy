# sender.py - The sender in the reliable data transfer protocol
import socket
import sys
import threading
import time
import udt
import packet

from timer import Timer

PACKET_SIZE = 512
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# Shared resources across threads
base = 0
send_timer = Timer(TIMEOUT_INTERVAL)
mutex = threading.Lock()

# Sets the window size
def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

# Send thread
def send(conn, data):
    global mutex
    global base
    global send_timer

    sock = conn.socket

    RECEIVER_ADDR = (conn.dest_ip, conn.dest_port)

    packets = create_pack_list(conn, data)
    num_packets = len(packets)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    # Start the receiver thread
    threading.Thread(target=receive, args=(sock,)).start()

    while base < num_packets:
        """
        - Enviar los mensajes en la ventana
        - Esperar mientras no se reciba el ACK
        - Reenviar los mensajes desde la base si da timeout
        - Recuerde utilizar mutex para las actualizaciones de base y send_timer
        - Use SLEEP_INTERVAL mientras espera recibir el ACK
        """
        mutex.acquire()
        # Send all the packets in the window
        while next_to_send < base + window_size:
            print('Sending packet', next_to_send)
            unpacked = packet.my_unpack(packets[next_to_send])
            print('ACK', unpacked.ack)
            udt.send(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        # Start the timer
        if not send_timer.running():
            print('Starting timer')
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            print('Sleeping')
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            # Looks like we timed out
            print('Timeout')
            send_timer.stop()
            next_to_send = base
        else:
            print('Shifting window')
            window_size = set_window_size(num_packets)
        mutex.release()

    print('last pack sent')
    # print('sending to', )
    # # Send empty packet as sentinel
    # udt.send(packet.Packet(), sock, RECEIVER_ADDR)
    
# Receive thread
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        pkt, _ = udt.recv(sock)
        ack_pack = packet.my_unpack(pkt)

        """
        - Actualizar la base
        - Detener el timer
        - Recuerde utilizar mutex para las actualizaciones
        """

        print('Got ACK', ack_pack.ack)
        if (ack_pack.ack >= base):
            mutex.acquire()
            base = ack_pack.ack + 1
            print('Base updated', base)
            send_timer.stop()
            mutex.release()

def create_pack_list(conn, data):
    packets = []

    count = 1
    seq_num = conn.seq_num 
    while True:
        start = (count - 1)*PACKET_SIZE
        end = min(count*PACKET_SIZE, len(data))
        d = data[start:end]
        pack = packet.create_send_packet(conn, d)
        packets.append(pack)
        count += 1
        seq_num += 1

        if end == len(data):
            break

    return packets