import trapy

conn = trapy.listen('10.0.0.2:8081')
trapy.accept(conn)
