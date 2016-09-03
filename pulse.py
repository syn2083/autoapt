import time
from logging_setup import init_logging, check_log

logger = init_logging()


class Pulse:
    def __init__(self):
        now = time.time()
        self.width = .25
        self.log_check = 100
        self._point = {'log_check': now + self.log_check}
        logger.debug('Now == %s (%f)', time.ctime(now), now)
        logger.debug('Tick len == %f', self.log_check)
        logger.debug('Tick time == %s (%f)', time.ctime(self._point['log_check']), self._point['log_check'])

    def perform_updates(self):
        now = time.time()
        if now >= self._point['log_check']:
            logger.debug('Checking log updates')
            check_log()
            self._point['log_check'] = time.time() + self.log_check
