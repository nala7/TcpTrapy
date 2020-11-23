# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt
import time


# Receive packets from the sender
def receive(conn, data):
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
        print('end', pack.is_end())
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