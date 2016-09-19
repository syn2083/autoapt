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
        self.command_queue = controller.command_queue
        self.proc_queue = controller.proc_queue
        self.demo_status = controller.demo_status

    def rec_data(self, conn):
        chunks = []

        while True:
            stream = conn.recv(config.CHUNK_SIZE)
            if stream == b'':
                break
            else:
                chunks.append(stream)
        return b''.join(chunks)

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
                logger.sock(in_data)
                if in_data[0] == 'demo control':
                    self.command_queue.append(in_data)
                else:
                    self.proc_queue.append(in_data)
                conn.close()
