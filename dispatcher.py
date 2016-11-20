import threading
import time
from logging_setup import init_logging
__author__ = 'Syn'

logger = init_logging()


class Dispatcher(threading.Thread):
    def __init__(self, controller):
        """
        Init the dispatcher thread, this is the gatekeeper, in my attempt to keep the application threadsafe.
        The dispatcher will never add to the deque, only popleft. It simply dispatches incoming payloads appropriately.
        :param controller: Allow the dispatcher access to the controller brain, to modify demo state.
        :type controller: controller.DemoController
        """
        super().__init__()
        self.controller = controller
        self.command_queue = controller.command_queue
        self.proc_queue = controller.proc_queue
        self.status_queue = controller.status_queue
        self.device_queue = controller.device_queue

    def run(self):
        """
        This is the main loop of the dispatcher, it is setup around the 2 deques, command_queue and proc_queue.
        self.command_queue will contain demo state controls, start/pause/stop and is independant of the job control
        queue. I did this to de-couple overall state logic from actual processing logic and allow for a paused demo
        to resume as is once a start request arrives.
        I set the while loop to run with a 250ms delay between actions, I do not need it to be any faster, and even this
        is likely overkill.
        :return: None
        :rtype: None
        """
        while True:
            payload = None
            try:
                payload = self.command_queue.popleft()
            except IndexError:
                pass
            if payload:

                if payload[0] == 'demo control':
                    if payload[1] == 'start':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Start demo request sent, but already started.')
                        elif self.controller.demo_status == 2:
                            logger.dispatch('Unpause Demo.')
                            self.controller.demo_status = 1
                            self.controller.resume_demo()
                        elif self.controller.demo_status == 0:
                            logger.dispatch('Starting Demo.')
                            self.controller.start_demo()
                            self.controller.demo_status = 1
                        else:
                            pass

                    if payload[1] == 'pause':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Pausing Demo.')
                            self.controller.demo_status = 2
                            self.controller.pause_demo()
                        elif self.controller.demo_status == 2:
                            pass
                        elif self.controller.demo_status == 0:
                            logger.dispatch('Pause sent to stopped demo, ignoring.')
                        else:
                            pass

                    if payload[1] == 'stop':
                        if self.controller.demo_status == 1:
                            logger.dispatch('Stopping Demo.')
                            self.controller.stop_demo()
                            self.controller.demo_status = 0
                        elif self.controller.demo_status == 2:
                            logger.dispatch('Stopping Demo.')
                            self.controller.stop_demo()
                            self.controller.demo_status = 0
                        elif self.controller.demo_status == 0:
                            logger.dispatch('Demo Stopped.')
                        else:
                            pass

                if payload[0] == 'job control':
                    if payload[1] == 'pause':
                        self.controller.pause_target(payload[2])
                    elif payload[1] == 'resume':
                        self.controller.resume_target(payload[2])
                    else:
                        pass

                if payload[0] == 'demo status':
                    if payload[1] == 'status_check':
                        self.controller.check_status(payload[2])

                payload = None

            if self.controller.demo_status == 1:
                try:
                    proc = self.proc_queue.popleft()
                    if proc(2) in ('job_proc_switch',):
                        logger.dispatch('Calling process change controller')
                        self.controller.proc_phase(proc)
                    if proc(2) in ('job_reprint', 'job_complete'):
                        logger.dispatch('Calling reprint controller from Proc Monitor')
                        self.controller.reprint_job(proc)
                    if proc(2) in ('job_received', 'job_failed'):
                        logger.dispatch('Calling new job controller')
                        self.controller.new_job(proc)
                except IndexError:
                    pass

                try:
                    device = self.device_queue.popleft()
                    if device[2] in ('device_enable', 'device_disable'):
                        logger.dispatch('Calling device state controller')
                        self.controller.device_state(device)
                    if device[2] in ('device_pause', 'device_resume'):
                        logger.dispatch('Calling device status controller')
                        self.controller.device_status(device)
                except IndexError:
                    pass

            if self.controller.demo_status == 2:
                pass

            if self.controller.demo_status == 0:
                try:
                    self.proc_queue.popleft()
                except IndexError:
                    pass
                try:
                    self.device_queue.popleft()
                except IndexError:
                    pass

            time.sleep(.250)
