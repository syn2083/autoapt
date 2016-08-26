__author__ = 'Syn'
import socket
import sys
import config
import json
from logging_setup import init_logging

logger = init_logging()


def client_handler(conn):
    request = json.loads(rec_data(conn))
    if 'demo control' == request[0]:
        if 'start' == request[1]:
            pass
        if 'stop' == request[1]:
            pass
        if 'pause' == request[1]:
            pass
    if 'demo config' == request[0]:
        if 'demo' == request[1]:
            pass
        if 'jif' == request[1]:
            pass
    if 'status check' == request[0]:
        pass


def rec_data(conn):
    chunks = []

    while True:
        stream = conn.recv(config.CHUNK_SIZE)
        if stream == b'':
            break
        else:
            chunks.append(stream)

    return b''.join(chunks)


def server_init():
    logger.debug('Socket Server initializing.')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((config.SERV_ADDR, config.SOCK_PORT))
        logger.debug('Server bound to {}, port {}'.format(config.SERV_ADDR, config.SOCK_PORT))
    except socket.error:
        logger.debug('Server bind failed. Error: '.format(sys.exc_info()))
        pass

    server.listen(5)
    logger.debug('---Server now listening---')

    return server


