import threading
from logging_setup import init_logging
__author__ = 'Syn'

logger = init_logging()


class Dispatcher(threading.Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.command_queue = controller.command_queue

    def run(self):
        while True:
            try:
                payload = self.command_queue.popleft()
                if payload[0] in ['Accepted', 'Failed']:
                    logger.dispatch('Calling new job controller')
                    self.controller.new_job(payload)
                if payload[0] in ['Reprint', 'Complete']:
                    self.controller.reprint_job(payload)
                if payload[0] in 'Proc':
                    self.controller.proc_phase(payload)
                if payload[0] == 'demo state':
                    if payload[1] == 'start':
                        logger.dispatch('Start Demo Request')
                        self.controller.start_demo()
                    if payload[1] == 'stop':
                        logger.dispatch('Stop Demo Request')
                        self.controller.stop_demo()
                    if payload[1] == 'pause':
                        logger.dispatch('Pause Demo Request')
                        pass
            except IndexError:
                pass
