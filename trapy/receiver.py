# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt
import time
import threading

from timer import Timer

TIMEOUT_INTERVAL = 0.5
END_CONN_INTERVAL = 5
end_conn_timer = False


# Shared resources across threads
base = 0
send_timer = Timer(TIMEOUT_INTERVAL)
mutex = threading.Lock()


# Receive packets from the sender
def receive(conn, data):
    threading.Thread(target=countdown, args=(END_CONN_INTERVAL,)).start()

    sock = conn.socket
    expected_num = conn.seq_num + 1
    recv_packets = []
    while True:
        # Get the next packet from the sender
        pack, addr = udt.recv(sock)
        pack = packet.my_unpack(pack)
        print(addr)

        # if not pack.check_checksum():
        #     print('check error')
        #     continue
        
        print('Got packet', pack.seq_num)
        # print(pack.data)
        if pack.is_end():
            close_pack = packet.create_close_packet(conn)
            udt.send(close_pack, sock, addr)
            print('CONNECTION CLOSED')
            return recv_packets

        # Send back an ACK
        if pack.seq_num == expected_num:
            print('Got expected packet')
            recv_packets.append(pack)
            print('Sending ACK', expected_num)
            ack_pack = packet.create_ack_packet(conn, expected_num)
            udt.send(ack_pack, sock, addr)
            print('Expected', expected_num)
            expected_num += 1
            # if pack.is_last_pack():
            #     print("last pack received")
            #     return recv_packets
        else:
            print('Sending ACK', expected_num - 1)
            ack_pack = packet.create_ack_packet(conn, expected_num - 1)
            udt.send(ack_pack, sock, addr)


    return recv_packets

def countdown(t): 
    global mutex
    global send_timer
    global end_conn_timer

    print('counting')
    while t > -1: 
        mutex.acquire()
        if not send_timer.running():
            mutex.release()
            return
        mutex.release()
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1
    mutex.acquire()
    send_timer.stop()
    end_conn_timer = True
    mutex.release()
    raise Exception('WAITING TIME EXCEDED')