import trapy

conn = trapy.listen('10.0.0.2:8080')
trapy.accept(conn)
trapy.recv(conn, 4096)
