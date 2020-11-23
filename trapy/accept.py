import trapy

conn = trapy.listen('10.0.0.2:8080')
conn_acc = trapy.accept(conn)
trapy.recv(conn_acc, 1024)
