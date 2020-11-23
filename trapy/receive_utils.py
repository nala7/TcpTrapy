import socket

def receiver(conn, len):
    while True:
        print('here')
        pack, _ = conn.socket.recvfrom(len)
        print(pack)