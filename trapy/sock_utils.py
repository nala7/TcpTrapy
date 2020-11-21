import socket

sender_sock_protocol = socket.SOCK_RAW 
receiver_sock_protocol = socket.IPPROTO_TCP


def create_sender_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, sender_sock_protocol)
    except socket.error:
        print('Sender raw socket could not be created')
    return sock

def create_receiver_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, receiver_sock_protocol)
    except socket.error:
        print('Receiver raw socket could not be created')
    return sock