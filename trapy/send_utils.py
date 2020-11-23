import packet

WINDOW_SIZE = 5
PACK_SIZE = 20
CURRENT_PACK = 0
UPPER_BASE = WINDOW_SIZE
BASE = 0
LEN_DATA = 0
seq_num = 0
ack = 0
    
def sender(conn, data : bytes):
    global BASE
    global LEN_DATA

    set_variables(conn, data)

    while BASE < LEN_DATA:
        print(BASE)
        pack = pack_to_send(conn, data)
        conn.socket.sendto(pack, ('10.0.0.2', 8080))
    print('sent')

def pack_to_send(conn, data):
    global WINDOW_SIZE
    global PACK_SIZE
    global CURRENT_PACK
    global BASE
    global UPPER_BASE
    global seq_num
    global ack

    flags = packet.create_flags()
    print('base', BASE)
    print('pack_size', PACK_SIZE)
    print('len', LEN_DATA)
    send_data = data[BASE:PACK_SIZE]
    pack = packet.Packet(conn.source_port, conn.dest_port, seq_num, ack, conn.source_ip, conn.dest_ip, flags, send_data)
    pack  = pack.pack()
    update_variables(pack, data)

    return pack

def update_variables(pack, data):
    global WINDOW_SIZE
    global PACK_SIZE
    global CURRENT_PACK
    global BASE
    global UPPER_BASE
    global LEN_DATA
    global seq_num
    global ack

    seq_num += 1
    ack += 1
    CURRENT_PACK += 1

    if CURRENT_PACK == UPPER_BASE:
        BASE = UPPER_BASE
        UPPER_BASE = min(UPPER_BASE + WINDOW_SIZE, UPPER_BASE + (LEN_DATA - UPPER_BASE))
        pack = packet.my_unpack(pack)
        PACK_SIZE = min(PACK_SIZE, pack.data_len)

def set_variables(conn, data):
    global WINDOW_SIZE
    global PACK_SIZE
    global UPPER_BASE
    global LEN_DATA
    global seq_num
    global ack

    LEN_DATA = len(data)
    seq_num = conn.seq_num
    ack = conn.ack

    if PACK_SIZE > LEN_DATA:
        PACK_SIZE = LEN_DATA
    
    if WINDOW_SIZE*PACK_SIZE > LEN_DATA:
        WINDOW_SIZE = LEN_DATA/PACK_SIZE
        UPPER_BASE = WINDOW_SIZE