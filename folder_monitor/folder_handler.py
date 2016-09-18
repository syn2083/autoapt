import os
import xmltodict
import time
from logging_setup import init_logging
from watchdog.events import PatternMatchingEventHandler


logger = init_logging()


class JIFAckHandler(PatternMatchingEventHandler):
    accept_pattern = ['*.accepted']
    fail_pattern = ['*.failed']

    def __init__(self, jifack_queue, lock):
        super().__init__()
        self.jifack_queue = jifack_queue
        self.lock = lock

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """

        full_filename = str(event.src_path).split('\\')[-1]
        job_id = full_filename.split('.')[0]
        result = full_filename.split('.')[-1]

        '''if 'accepted' in result:
            logger.debug('JIF ACK - Accepted Job {}'.format(job_id))
            # self.lock.acquire()
            self.jifack_queue.append(['Accepted', job_id])
            # self.lock.release()'''

        if 'failed' in result:
            logger.debug('JIF ACK - Failed Job {}'.format(job_id))
            # self.lock.acquire()
            self.jifack_queue.append(['Failed', job_id])
            # self.lock.release()

    def on_modified(self, event):
        logger.io('Saw creation {}'.format(event.src_path))
        self.process(event)


class ReprintHandler(PatternMatchingEventHandler):
    reprint_pattern = ['*.txt']

    def __init__(self, reprint_queue, lock):
        super().__init__()
        self.reprint_queue = reprint_queue
        self.lock = lock

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        full_filename = str(event.src_path).split('\\')[-1]
        job_id = full_filename.split('.')[0]
        time.sleep(2)

        if os.path.getsize(event.src_path) == 0:
            logger.debug('Reprint - Completed Job {}'.format(job_id))
            # self.lock.acquire()
            self.reprint_queue.append(['Complete', job_id])
            # self.lock.release()
        else:
            logger.debug('Reprint - Reprint Job {}'.format(job_id))
            # self.lock.acquire()
            self.reprint_queue.append(['Reprint', job_id])
            # self.lock.release()

    def on_created(self, event):
        self.process(event)


class ProcChangeManager(PatternMatchingEventHandler):
    proc_pattern = ['*.xml']

    def __init__(self, proc_queue, lock):
        super().__init__()
        self.proc_queue = proc_queue
        self.lock = lock

    def modified_process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        xml_string = None
        never_proc = 1
        reprint = 8
        complete = 64
        full_filename = str(event.src_path).split('\\')[-1]

        while True:
            try:
                with open(event.src_path, 'r') as xml_source:
                    x = xml_source.read()
                xml_string = xmltodict.parse(x)
                break
            except:
                pass

        if full_filename.split('.')[1] == 'JOB_STATUS_CHANGE':
            element = dict(xml_string.get('EventOutput', {}).get('Job', {}))
            if element['ID'][:2] == 'A1':
                if element['JobStatus'] == '1026' or element['JobStatus'] == '1030':
                    logger.debug('Proc Mon - Multi-Step Print Finished Job {}'.format(element['ID']))
                    # self.lock.acquire()
                    self.proc_queue.append(['Proc', element['ID']])
                    # self.lock.release()
            if int(element['JobStatus']) & reprint:
                logger.debug('Proc Mon - Reprint found for job {}'.format(element['ID']))
                self.proc_queue.append(['Reprint', element['ID']])
        if full_filename.split('.')[1] == 'JOB_DONE':
            element = dict(xml_string.get('EventOutput', {}).get('Job', {}))
            if int(element['JobStatus']) & complete:
                logger.debug('Proc Mon - Complete found for job {}'.format(element['ID']))
                self.proc_queue.append(['Complete', element['ID']])
        if full_filename.split('.')[1] == 'NEW_JOB_RECEIVED':
            element = dict(xml_string.get('EventOutput', {}).get('Job', {}))
            if int(element['JobStatus']) & never_proc:
                logger.debug('Proc Mon - New Job Found for job {}'.format(element['ID']))
                self.proc_queue.append(['Accepted', element['ID']])


    def on_created(self, event):
        pass

    def on_modified(self, event):
        self.modified_process(event)
