"""
MIT License, apllicable to all parts of this project that are not external imports.

Copyright (c) 2016 Tim Rogers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__author__ = 'Syn'
import utilities
from webinterface import aptinterface
from logging_setup import init_logging
from init import init_controller
from server import SocketServer

logger = init_logging()


def autoapt():
    """
    System intilization method. Starts all necesarry components to run the system:
    Controller == central intelligence
    SocketServer == Threaded TCP Socket server
    Web_server == flask interface with some instructions and controls for the system.
    Also cleans old data out of some APT folder locations to keep hdd footprint low for APT.
    :return:
    :rtype:
    """
    logger.boot('--System Booting--')
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
