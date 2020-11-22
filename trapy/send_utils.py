WINDOW_SIZE = 4
base = 0

def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)
    
def sender(conn, data : bytes):
    pass