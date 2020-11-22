WINDOW_SIZE = 20
base = 0

def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)
    
def sender(conn, data : bytes):
    global base

    while base < len(data):
        pack = pack_to_send(data)

        conn.socket.sendto(pack, ('10.0.0.2', 8080))
    print('sent')

def pack_to_send(data):
    global base
    set_window_size(data)
    pack = data[base:WINDOW_SIZE]
    base += WINDOW_SIZE
    return pack


def set_window_size(data):
    global WINDOW_SIZE
    global base

    if WINDOW_SIZE + base > len(data):
        WINDOW_SIZE += WINDOW_SIZE + base - len(data)

