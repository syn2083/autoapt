import threading
import time
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
            if self.controller.demo_status == 2:
                try:
                    for payload in self.command_queue:
                        if payload[0] == 'demo control':
                            if payload[1] == 'start':
                                self.controller.demo_status = 1
                            elif payload[1] == 'stop':
                                self.controller.demo_status = 0
                            elif payload[1] == 'reset_seed':
                                pass
                            else:
                                pass
                except IndexError:
                    pass
            elif self.controller.demo_status == 0:
                if len(self.command_queue) >= 1:
                    try:
                        payload = self.command_queue.popleft()
                        if payload[0] == 'demo control':
                            if payload[1] == 'start':
                                logger.dispatch('Start Demo Request')
                                self.controller.start_demo()
                                self.controller.demo_status = 1
                            elif payload[1] == 'reset_seed':
                                self.controller.reset_seed()
                        else:
                            pass
                    except IndexError:
                        pass
                else:
                    pass
            else:
                try:
                    payload = self.command_queue.popleft()
                    if payload[0] in ['Accepted', 'Failed']:
                        logger.dispatch('Calling new job controller')
                        self.controller.new_job(payload)
                    if payload[0] in ['Reprint', 'Complete']:
                        self.controller.reprint_job(payload)
                    if payload[0] in 'Proc':
                        self.controller.proc_phase(payload)
                    if payload[0] == 'demo control':
                        if payload[1] == 'start':
                            if self.controller.demo_status is not 1:
                                logger.dispatch('Start Demo Request')
                                self.controller.start_demo()
                                self.controller.demo_status = 1
                            else:
                                logger.dispatch('Start request when already started, ignored.')
                        if payload[1] == 'stop':
                            logger.dispatch('Stop Demo Request')
                            self.controller.stop_demo()
                        if payload[1] == 'pause':
                            logger.dispatch('Pause Demo Request')
                            self.controller.demo_status = 2
                            pass
                        if payload[1] == 'reset_seed':
                            pass
                except IndexError:
                    pass
            time.sleep(1)
