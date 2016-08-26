__author__ = 'Syn'
import socket
import json

TCP_IP = '127.0.0.1'
TCP_PORT = 8091
BUFFER_SIZE = 4096
MESSAGE = "Hello, World!"
eod = '-eod'

t = json.dumps({'Test': 'me', 1: 3})

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.sendall(t.encode('utf-8'))
s.close()
