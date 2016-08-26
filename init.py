__author__ = 'Syn'
import server
import json
from logging_setup import init_logging

logger = init_logging()

if __name__ == '__main__':
    logger.debug('--Socket Server startup called--')
    serv = server.server_init()

    while True:
        conn, addr = serv.accept()

        if conn:
            logger.debug('Connection established from {}:{}'.format(addr[0], addr[1]))


        conn.close()
