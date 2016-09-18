__author__ = 'Syn'
import utilities
from webinterface import aptinterface
from logging_setup import init_logging
from init import init_controller
from server import SocketServer

logger = init_logging()


def autoapt():
    logger.boot('--System Booting--')
    # start_snapshot = utilities.ResourceSnapshot()
    # logger.boot(start_snapshot.log_data())
    logger.boot('--Starting AutoAPT Controller--')
    control = init_controller()
    logger.sock('--Socket Server Initialization--')
    control.socket_server = SocketServer(control)
    control.socket_server.start()
    logger.boot('--Cleaning Reprint Directory--')
    cleaned_reprint_files = utilities.clean_reprints(control)
    logger.boot('Removed {} files from APT Reprint Folder.'.format(cleaned_reprint_files))
    logger.boot('--Cleaning TD Directory--')
    cleaned_td_files = utilities.clean_td(control)
    logger.boot('Removed {} files from APT TD Folder.'.format(cleaned_td_files))
    logger.debug('JDF {}'.format(control.jif_folder))
    logger.boot('--Starting Web Interface--')
    web_server = aptinterface.app
    web_server.run(host='127.0.0.1', port=8080)
    logger.boot('--System Startup Complete, Entering Main Loop--')

if __name__ == '__main__':
    autoapt()
