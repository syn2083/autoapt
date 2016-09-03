__author__ = 'Syn'
import socket
import json

TCP_IP = '127.0.0.1'
TCP_PORT = 8091

t = json.dumps(['demo control', 'start'])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.sendall(t.encode('utf-8'))
s.close()
