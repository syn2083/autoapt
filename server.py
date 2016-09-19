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
        """
        The socketserver thread. With my limited understanding of threading, and obvious problems trying to run the
        socketserver directly in a main app loop, I decided to pass the socketserver into it's own thread. It contains
        the deques needed to add incoming payloads appropriately for the dispatcher to then deal with later.
        :param controller:
        :type controller: controller.DemoController
        """
        super().__init__()
        self.command_queue = controller.command_queue
        self.proc_queue = controller.proc_queue
        self.demo_status = controller.demo_status

    def rec_data(self, conn):
        """
        Based on examples and tutorials, the rec_data method.
        :param conn:
        :type conn: socket.socket
        :return: bytestring containing json payload
        :rtype: bytes
        """
        chunks = []

        while True:
            stream = conn.recv(config.CHUNK_SIZE)
            if stream == b'':
                break
            else:
                chunks.append(stream)
        return b''.join(chunks)

    def server_init(self):
        """
        Initialize the socketserver with values from config.py.
        :return: initialized and bound SocketServer.server
        :rtype: socket.socket
        """
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
        """
        Worker process for the socketserver, loops looking for connections, and handles any incoming request.
        Passes off to rec_data, and then json.loads resultant bytestring.
        Passes the payload to either self.command_queue or self.proc_queue depending on payload contents.
        :return: None
        :rtype: None
        """
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
