__author__ = 'Syn'
import socket
import json
from logging_setup import init_logging

logger = init_logging()

"""Backup method to starting the demo system if webinterface is not working for some reason."""

TCP_IP = '127.0.0.1'
TCP_PORT = 8091

k = ['Accepted', 'A400000056']

def sock_connect(jdump):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.sendall(jdump.encode('utf-8'))
    s.close()


def console_input(in_data):
    if 'start' in in_data:
        t = json.dumps(['demo control', 'start'])
        sock_connect(t)
    elif 'stop' in in_data:
        t = json.dumps(['demo control', 'stop'])
        sock_connect(t)
    else:
        logger.error('Unknown console command: {}'.format(in_data))


if __name__ == '__main__':
    sock_connect(json.dumps(k))
