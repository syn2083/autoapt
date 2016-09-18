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
        self.reprint_queue = controller.reprint_queue
        self.jifack_queue = controller.jifack_queue
        self.proc_queue = controller.proc_queue

    def run(self):
        while True:
            try:
                payload = self.command_queue.popleft()
                if payload[0] == 'demo control':
                    if payload[1] == 'start':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Start demo request sent, but already started.')
                        if self.controller.demo_status == 2:
                            logger.dispatch('Unpause Demo.')
                            self.controller.demo_status = 1
                        if self.controller.demo_status == 0:
                            logger.dispatch('Starting Demo.')
                            self.controller.start_demo()
                            self.controller.demo_status = 1
                    if payload[1] == 'pause':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Pausing Demo.')
                            self.controller.demo_status = 2
                        if self.controller.demo_status == 2:
                            logger.dispatch('Resuming Demo.')
                            self.controller.demo_status = 1
                        if self.controller.demo_status == 0:
                            logger.dispatch('Pause sent to stopped demo, ignoring.')
                    if payload[1] == 'stop':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Stopping Demo.')
                            self.controller.stop_demo()
                            self.controller.demo_status = 0
                        if self.controller.demo_status == 2:
                            logger.dispatch('Resuming Demo.')
                            self.controller.demo_status = 1
                        if self.controller.demo_status == 0:
                            logger.dispatch('Demo Stopped.')
            except IndexError:
                pass
            if self.controller.demo_status == 1:
                try:
                    jifack = self.jifack_queue.popleft()
                    if jifack[0] in ['Accepted', 'Failed']:
                        logger.dispatch('Calling new job controller')
                        self.controller.new_job(jifack)
                except IndexError:
                    pass
                try:
                    # reprint = self.reprint_queue.popleft()
                    self.reprint_queue.popleft()
                    # if reprint[0] in ['Reprint', 'Complete']:
                        # logger.dispatch('Calling reprint controller')
                        # self.controller.reprint_job(reprint)
                except IndexError:
                    pass
                try:
                    proc = self.proc_queue.popleft()
                    if proc[0] in ['Proc']:
                        logger.dispatch('Calling process change controller')
                        self.controller.proc_phase(proc)
                    if proc[0] in ['Reprint', 'Complete']:
                        logger.dispatch('Calling reprint controller from Proc Monitor')
                        self.controller.reprint_job(proc)
                    if proc[0] in ['Accepted', 'Failed']:
                        logger.dispatch('Calling new job controller')
                        self.controller.new_job(proc)
                except IndexError:
                    pass
            if self.controller.demo_status == 2:
                pass
            if self.controller.demo_status == 0:
                try:
                    self.jifack_queue.popleft()
                except IndexError:
                    pass
                try:
                    self.reprint_queue.popleft()
                except IndexError:
                    pass
                try:
                    self.proc_queue.popleft()
                except IndexError:
                    pass
            time.sleep(.250)
