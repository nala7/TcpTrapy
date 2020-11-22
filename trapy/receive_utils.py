import socket

def receiver(conn, len):
    print('here')
    pack, _ = conn.socket.recvfrom(len)
    print(pack)