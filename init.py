__author__ = 'Syn'
import server
import utilities
import time
#from controller import DemoController
from pulse import Pulse
from logging_setup import init_logging

logger = init_logging()

if __name__ == '__main__':
    logger.info('--System Booting--')
    snap, startup = utilities.sys_snapshot()
    logger.info('-System Snapshot\n{}'.format(startup))
    logger.info('--Socket Server Initialization-')
    serv = server.server_init()
    demc, jifc = utilities.init_configs()
    logger.info('--Pulse Updater Initialization--')
    pulse = Pulse()
    # control = DemoController(demc)
    logger.info('--System Startup Complete, Entering Main Loop--')
    while True:
        conn, addr = serv.accept()
        pulse.perform_updates()
        if conn:
            logger.info('Connection established from {}:{}'.format(addr[0], addr[1]))
        conn.close()
