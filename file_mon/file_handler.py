__author__ = 'Syn'
import time
import xmltodict
import threading
from watchdog.events import PatternMatchingEventHandler
from logging_setup import init_logging

logger = init_logging()


def data_processor(trigger, path, queue):
    time.sleep(.5)
    if trigger == 'Proc':
        status_file = None

        try:
            with open(path, 'r') as fp:
                status_file = fp.read()
        except FileNotFoundError:
            logger.io('File not found in StatusChange')

        event_dict = xmltodict.parse(status_file)
        job_dict = event_dict['EventOutput']['Job']

        if job_dict['JobStatus'] in ('1026', '1030'):
            queue.append(['Proc', job_dict['ID'], int(job_dict['JobStatus'])])
        else:
            pass

    elif trigger == 'Accepted':
        full_filename = str(path).split('\\')[-1]
        jobid = full_filename.split('.')[0]
        queue.append(['Accepted', jobid])

    elif trigger == 'Reprint':
        full_filename = str(path).split('\\')[-1]
        jobid = full_filename.split('.')[0]
        queue.append(['Reprint', jobid])

    elif trigger == 'Complete':
        full_filename = str(path).split('\\')[-1]
        jobid = full_filename.split('.')[0]
        queue.append(['Complete', jobid])

    else:
        logger.io('File monitor processor called, but trigger does not match expected {}'.format(trigger))


class StatusChange(PatternMatchingEventHandler):
    patterns = ['*.JOB_STATUS_CHANGE.xml']

    def __init__(self, proc_queue):
        super().__init__()
        self.proc_queue = proc_queue
        self.active_threads = []

    def on_modified(self, event):
        logger.io('Status change event')
        worker = threading.Thread(target=data_processor, args=('Proc', event.src_path, self.proc_queue))
        self.active_threads.append(worker)
        worker.start()


class NewJob(PatternMatchingEventHandler):
    patterns = ['*.NEW_JOB_RECEIVED.xml']

    def __init__(self, proc_queue):
        super().__init__()
        self.proc_queue = proc_queue
        self.active_threads = []

    def on_created(self, event):
        logger.io('Accepted job event')
        worker = threading.Thread(target=data_processor, args=('Accepted', event.src_path, self.proc_queue))
        self.active_threads.append(worker)
        worker.start()


class Reprint(PatternMatchingEventHandler):
    patterns = ['*.JOB_REPRINT_SENT.xml']

    def __init__(self, proc_queue):
        super().__init__()
        self.proc_queue = proc_queue
        self.active_threads = []

    def on_created(self, event):
        logger.io('Reprint job event')
        worker = threading.Thread(target=data_processor, args=('Reprint', event.src_path, self.proc_queue))
        self.active_threads.append(worker)
        worker.start()


class Completed(PatternMatchingEventHandler):
    patterns = ['*.JOB_DONE.xml']

    def __init__(self, proc_queue):
        super().__init__()
        self.proc_queue = proc_queue
        self.active_threads = []

    def on_created(self, event):
        logger.io('Completed job event')
        worker = threading.Thread(target=data_processor, args=('Complete', event.src_path, self.proc_queue))
        self.active_threads.append(worker)
        worker.start()
