# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt


# Receive packets from the sender
def receive(conn, data):
    sock = conn.socket
    expected_num = conn.ack + 1
    print('fuera del while')
    while True:
        # Get the next packet from the sender
        pack, addr = udt.recv(sock)
        pack = packet.my_unpack(pack)

        # if not pack.check_checksum():
        #     print('check error')
        #     continue
        
        print('Got packet', pack.seq_num)
        # print(pack.data)
        
        # Send back an ACK
        if pack.seq_num == expected_num:
            print('Got expected packet')
            print('Sending ACK', expected_num)
            ack_pack = packet.create_ack_packet(conn, expected_num)
            udt.send(ack_pack, sock, addr)
            expected_num += 1
            print('Expected', expected_num)
            print(data)
        else:
            print('Sending ACK', expected_num - 1)
            ack_pack = packet.create_ack_packet(conn, expected_num - 1)
            udt.send(ack_pack, sock, addr)