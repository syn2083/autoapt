import logging
import os
import config
from logging.handlers import RotatingFileHandler

master_logger = None


def boot_log(self, message, *args, **kws):
    if self.level <= 31:
        self._log(31, message, args, **kws)


def socket_log(self, message, *args, **kws):
    if self.level <= 30:
        self._log(30, message, args, **kws)


def demo_state(self, message, *args, **kws):
    if self.level <= 29:
        self._log(29, message, args, **kws)


def io_handler(self, message, *args, **kws):
    if self.level <= 28:
        self._log(28, message, args, **kws)


def jifgen(self, message, *args, **kws):
    if self.level <= 27:
        self._log(27, message, args, **kws)


def dispatch(self, message, *args, **kws):
    if self.level <= 26:
        self._log(26, message, args, **kws)


def init_logging():
    global master_logger
    if master_logger is None:
        if not os.path.exists(config.log_dir):
            os.makedirs(config.log_dir)
            with open(config.log_file, 'w') as fp:
                fp.write('---Logging Init---')
        handler = RotatingFileHandler(filename='{}'.format(config.log_file), maxBytes=524288, backupCount=10)
        streamer = logging.StreamHandler()
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(levelname)-11s] %(asctime)s %(module)14s| %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[handler, streamer])
        logging.addLevelName(31, 'BOOT')
        logging.addLevelName(30, 'SOCK_SERVER')
        logging.addLevelName(29, 'DEMO_STATE')
        logging.addLevelName(28, 'IO_HANDLER')
        logging.addLevelName(27, 'JIFGEN')
        logging.addLevelName(26, 'DISPATCH')
        logging.Logger.boot = boot_log
        logging.Logger.sock = socket_log
        logging.Logger.demo = demo_state
        logging.Logger.io = io_handler
        logging.Logger.jifgen = jifgen
        logging.Logger.dispatch = dispatch
        master_logger = logging.getLogger()
    return master_logger
