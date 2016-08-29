import os
import xmltodict
from logging_setup import init_logging
from watchdog.events import PatternMatchingEventHandler

logger = init_logging()


class JIFAckHandler(PatternMatchingEventHandler):
    accept_pattern = ['*.accepted']
    fail_pattern = ['*.failed']

    def __init__(self, command_queue, lock):
        super().__init__()
        self.command_queue = command_queue
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

        if 'accepted' in result:
            logger.debug('JIF ACK - Accepted Job {}'.format(job_id))
            self.lock.acquire()
            self.command_queue.append(['Accepted', job_id])
            self.lock.release()

        if 'failed' in result:
            logger.debug('JIF ACK - Failed Job {}'.format(job_id))
            self.lock.acquire()
            self.command_queue.append(['Failed', job_id])
            self.lock.release()

    def on_created(self, event):
        self.process(event)


class ReprintHandler(PatternMatchingEventHandler):
    reprint_pattern = ['*.txt']

    def __init__(self, command_queue, lock):
        super().__init__()
        self.command_queue = command_queue
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

        if os.path.getsize(event.src_path) == 0:
            logger.debug('Reprint - Completed Job {}'.format(job_id))
            self.lock.acquire()
            self.command_queue.append(['Complete', job_id])
            self.lock.release()
        else:
            logger.debug('Reprint - Reprint Job {}'.format(job_id))
            self.lock.acquire()
            self.command_queue.append(['Reprint', job_id])
            self.lock.release()

    def on_created(self, event):
        self.process(event)


class ProcChangeManager(PatternMatchingEventHandler):
    reprint_pattern = ['*.xml']

    def __init__(self, command_queue, lock):
        super().__init__()
        self.command_queue = command_queue
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
        xml_string = None
        while True:
            try:
                with open(event.src_path, 'r') as xml_source:
                    x = xml_source.read()
                xml_string = xmltodict.parse(x)
                break
            except:
                pass

        element = dict(xml_string.get('EventOutput', {}).get('Job', {}))
        if element['ID'][:2] == 'A1':
            if element['JobStatus'] == '1026' or element['JobStatus'] == '1030':
                logger.debug('Proc Mon - Multi-Step Print Finished Job {}'.format(element['ID']))
                self.lock.acquire()
                self.command_queue.append(['Proc', element['ID']])
                self.lock.release()

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)
