__author__ = 'Syn'
import socket
import sys
import config
import json
import threading
from logging_setup import init_logging

logger = init_logging()


class SocketServer(threading.Thread):
    def __init__(self, controller):
        super().__init__()
        self.lock = controller.lock
        self.command_queue = controller.command_queue

    def rec_data(self, conn):
        chunks = []

        while True:
            stream = conn.recv(config.CHUNK_SIZE)
            if stream == b'':
                break
            else:
                chunks.append(stream)
        return b''.join(chunks)

    def client_handler(self, conn):
        request = json.loads(self.rec_data(conn))
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

    def server_init(self):
        logger.sock('Socket Server initializing.')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server.bind((config.SERV_ADDR, config.SOCK_PORT))
            logger.sock('Server bound to {}, port {}'.format(config.SERV_ADDR, config.SOCK_PORT))
        except socket.error:
            logger.sock('Server bind failed. Error: '.format(sys.exc_info()))
            pass

        server.listen(5)
        logger.sock('---Server now listening---')

        return server

    def run(self):
        socket_server = self.server_init()

        while True:
            conn, addr = socket_server.accept()
            if conn:
                logger.sock('Connection established from {}:{}'.format(addr[0], addr[1]))
                in_data = json.loads(self.rec_data(conn).decode('utf-8'))
                logger.sock('Incoming data: {}'.format(in_data))
                self.lock.acquire()
                logger.sock(in_data)
                self.command_queue.append(in_data)
                self.lock.release()
                conn.close()



