__author__ = 'Syn'
import utilities
import time
from webinterface import aptinterface
from logging_setup import init_logging
from init import init_controller
from server import SocketServer
from pulse import Pulse

logger = init_logging()


def autoapt():
    logger.boot('--System Booting--')
    start_snapshot = utilities.ResourceSnapshot()
    logger.boot(start_snapshot.log_data())
    logger.sock('--Socket Server Initialization-')
    logger.info('--Pulse Updater Initialization--')
    pulse = Pulse()
    control = init_controller()
    control.socket_server = SocketServer(control)
    control.socket_server.start()
    logger.boot('--Cleaning Reprint Directory--')
    clean_files = utilities.clean_reprints(control)
    logger.boot('Removed {} files from APT Reprint Folder.'.format(clean_files))
    logger.debug('JDF {}'.format(control.jif_folder))
    logger.boot('--Starting Web Interface--')
    web_server = aptinterface.app
    web_server.run(host='127.0.0.1', port=8080)
    logger.boot('--System Startup Complete, Entering Main Loop--')

    while True:
        top_of_loop = time.time()
        pulse.perform_updates()
        time_spent = time.time() - top_of_loop
        nap_time = pulse.width - time_spent
        if nap_time > 0.0:
            time.sleep(nap_time)
        else:
            logger.warn('Exceeded time slice by %.3f seconds!', abs(nap_time))

if __name__ == '__main__':
    autoapt()
