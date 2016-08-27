__author__ = 'Syn'
import server
import utilities
import time
from controller import DemoController
from pulse import Pulse
from logging_setup import init_logging

logger = init_logging()


def autoapt():
    logger.boot('--System Booting--')
    start_snapshot = utilities.ResourceSnapshot()
    logger.boot(start_snapshot.log_data())
    logger.sock('--Socket Server Initialization-')
    serv = server.server_init()
    demc, jifc = utilities.init_configs()
    logger.info('--Pulse Updater Initialization--')
    pulse = Pulse()
    control = DemoController(demc, jifc)
    logger.boot('--System Startup Complete, Entering Main Loop--')
    while True:
        top_of_loop = time.time()
        # conn, addr = serv.accept()
        pulse.perform_updates()
        # if conn:
        # logger.info('Connection established from {}:{}'.format(addr[0], addr[1]))
        # conn.close()
        time_spent = time.time() - top_of_loop
        nap_time = pulse.width - time_spent
        if nap_time > 0.0:
            time.sleep(nap_time)
        else:
            logger.warn('Exceeded time slice by %.3f seconds!', abs(nap_time))

if __name__ == '__main__':
    autoapt()
