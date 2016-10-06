import os
import shutil
import threading
import time
import random
import json
from collections import deque
from logging_setup import init_logging
from jifgenerator import jif_assembler

"""
This is the Demo Controller Brain.
"""
logger = init_logging()


class DataWorker(threading.Thread):
    def __init__(self, job_queue, spr, exit_dir, target):
        threading.Thread.__init__(self)
        self.paused = False
        self._pause_cond = threading.Condition(threading.Lock())
        self.spr = spr
        self.exit_dir = exit_dir
        self.target = target
        self.job_queue = job_queue
        self.interval = None

    def find_files(self, jobid):
        output_files = []
        file_dump = [f for f in os.listdir(self.exit_dir) if jobid in f if self.spr in f]

        for ind in range(0, len(file_dump)):
            for file in file_dump:
                if ind == int(file.split('.')[2]):
                    output_files.append(file)
        if self.spr == 'sheet':
            interval = int(file_dump[0].split('.')[1])
            if interval > 5:
                interval -= 5
        else:
            interval = int(file_dump[0].split('.')[1]) + 2
        
        return output_files, interval

    def run(self):
        running = True
        jobid = None

        while running:
            try:
                jobid = self.job_queue.popleft()
            except IndexError:
                pass
            if jobid:
                # logger.io('New jobid in {}'.format(jobid))
                # Add a little variation to when files start copying
                time.sleep(random.randint(10, 30))
                files, interval = self.find_files(jobid)
                # logger.io(files)
                with self._pause_cond:
                    for file in files:
                        try:
                            original_loc = os.path.join(self.exit_dir, file)
                            target_loc = os.path.join(self.target, file)
                            # logger.io('Copying data file {}'.format(file))
                            shutil.copyfile(original_loc, target_loc)
                        except FileNotFoundError:
                            interval = 0
                        while self.paused:
                            self._pause_cond.wait()
                        time.sleep(interval)
                    jobid = None
            time.sleep(.5)

    def pause(self):
        self.paused = True
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self._pause_cond.acquire()

    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self._pause_cond.notify()
        # Now release the lock
        self._pause_cond.release()


class DataController:
    def __init__(self, all_targets, reprint_targets, target_data, exit_dir):
        self.all_targets = {k: None for k in all_targets}
        self.reprints = reprint_targets
        self.exit_dir = exit_dir
        for i in target_data.keys():
            setattr(self, i, target_data[i])

    def setup_workers(self):
        for target in self.all_targets.keys():
            new_queue = deque()
            new_thread = DataWorker(new_queue, getattr(self, target)['piece_or_sheet'], self.exit_dir,
                                    getattr(self, target)['path'])
            self.all_targets[target] = [new_queue, new_thread]
            
            new_thread.start()
            logger.io('Worker threads initialized.')

    def new_data(self, jobid, target_device):
        logger.io('Data controller, target {}'.format(target_device))
        self.all_targets[target_device][0].append(jobid)
        logger.io('Deque {}'.format(self.all_targets[target_device][0]))

    def pause_worker(self, worker):
        if isinstance(worker, list):
            try:
                for i in worker:
                    logger.io('Pausing worker: {}'.format(i))
                    self.all_targets[i][1].pause()
            except ValueError:
                logger.debug('Blank list passed to pause_worker.')
        else:
            logger.io('Pausing worker: {}'.format(worker))
            self.all_targets[worker][1].pause()

    def resume_work(self, worker):
        if isinstance(worker, list):
            try:
                for i in worker:
                    logger.io('Resuming work: {}'.format(i))
                    self.all_targets[i][1].resume()
            except ValueError:
                logger.debug('Blank list passed to resume_work.')
        else:
            logger.io('Resuming work: {}'.format(worker))
            self.all_targets[worker][1].resume()

    def clear_queues(self):
        logger.io('Clearing worker queues.')
        for worker in self.all_targets.values():
            worker[0].clear()


class DemoController:
    def __init__(self, dconf, jconf, sysconf):
        """
        Init the Demo Controller, taking in the JIF Config object, and Demo Config object
        :param dconf: 
        :type dconf: List[Dict[str, Dict[str, int]]]
        :param jconf: 
        :type jconf: List[Dict[str, Dict[str, str]]]
        """
        self.demo_status = 0
        for k in dconf[0].keys():
            setattr(self, k, dconf[0][k])
        for k in dconf[2].keys():
            setattr(self, k, dconf[2][k])
        self.monitors = []
        self.clients = None
        self.lock = None
        self.dispatcher = None
        self.observers = []
        self.socket_server = None
        self.data_controller = None
        self.command_queue = deque()
        self.proc_queue = deque()
        self.status_queue = deque()
        self.active_jobs = {}
        self.completed_jobs = []
        self.reprinting_jobs = []
        self.data_workers = []
        self.paused_td = None
        self.exit_dir = dconf[1]['DemoDirs']['exit_data']
        self.jif_data = dconf[1]['DemoDirs']['jif_data']
        self.jif_folder = dconf[1]['APTDirs']['jdf']
        self.reprint_folder = dconf[1]['APTDirs']['reprint']
        self.proc_dir = dconf[1]['APTDirs']['proc']
        self.first_run = 1
        self.num_jobs = 0
        self.target_dirs = {k: dconf[0][k]['path'] for k in dconf[0].keys()}
        self.jifconfig = jconf
        self.democonf = dconf
        self.sysconf = sysconf

    def __repr__(self):
        """
        :return: current demo status as a string for future web representation. 
        :rtype: str
        """
        if self.demo_status == 0:
            return 'Not Running'
        if self.demo_status == 1:
            return 'Running'
        if self.demo_status == 2:
            return 'Paused'

    def pause_demo(self):
        logger.demo('Sending pause signal to data controller.')
        self.data_controller.pause_worker(self.all_targets)
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'message', 'value': 'Paused'}))
            client.write_message(json.dumps({'id': 'td', 'value': 'Paused'}))

    def resume_demo(self):
        logger.demo('Sending resume signal to data controller.')
        self.data_controller.resume_work(self.all_targets)
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'message', 'value': 'Running'}))
            client.write_message(json.dumps({'id': 'td', 'value': 'Running'}))

    def pause_target(self, target):
        logger.demo('Pausing single target, sending signal to data controller.')
        self.data_controller.pause_worker(target)
        self.paused_td = True
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'td', 'value': 'Paused'}))

    def resume_target(self, target):
        logger.demo('Resuming single target, sending signal to data controller.')
        self.data_controller.resume_work(target)
        self.paused_td = None
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'td', 'value': 'resume'}))

    def check_status(self, websocket):
        logger.demo('Websocket status check for {}'.format(websocket))
        try:
            if self.demo_status == 0:
                self.clients[websocket].write_message(json.dumps({'id': 'message', 'value': 'Stopped'}))
                self.clients[websocket].write_message(json.dumps({'id': 'td', 'value': 'Stopped'}))
            if self.demo_status == 1:
                self.clients[websocket].write_message(json.dumps({'id': 'message', 'value': 'Running'}))
                if self.paused_td:
                    self.clients[websocket].write_message(json.dumps({'id': 'td', 'value': 'Paused'}))
                else:
                    self.clients[websocket].write_message(json.dumps({'id': 'td', 'value': 'Running'}))
            if self.demo_status == 2:
                self.clients[websocket].write_message(json.dumps({'id': 'message', 'value': 'Paused'}))
                self.clients[websocket].write_message(json.dumps({'id': 'td', 'value': 'Paused'}))
            self.clients[websocket].write_message(json.dumps({'id': 'jobs', 'value': '{}'.format(self.num_jobs)}))
        except KeyError:
            logger.demo('Tried a status check on non-existant websocket entry.')

    def create_job(self, origin):
        """
        DRY.. job creator helper method. Adds new job to active jobs, and adds the jobid to the origins list as well.
        :param origin: string representation of origin ICD
        :type origin: str
        :return: string representation of new jobid if needed in the future.
        :rtype: str
        """
        gen = jif_assembler.JIFBuilder(origin, self.jif_folder, self.democonf, self.jifconfig)
        logger.io('Creating {} JIF/Exit Data'.format(origin.upper()))
        new_job = gen.gen_jifs()
        getattr(self, origin)['jobid'].append(new_job)
        self.active_jobs[new_job] = [origin, origin]
        self.num_jobs += 1
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'jobs', 'value': '{}'.format(self.num_jobs)}))
        return new_job

    def reset_seed(self):
        """
        Method for a flask call to reset jifgenerator seed to 1, effectively restarting demo.
        :return: String confirming reset for web display
        :rtype: str
        """
        scriptdir, script = os.path.split(__file__)
        seed_loc = os.path.join(scriptdir, 'jifgenerator/job_seed.txt')
        logger.demo('Resetting job seed to 1')
        with open(seed_loc, 'w') as fp:
            fp.write('1')
        return 'Reset job seed to 1'

    def start_demo(self):
        """
        Clean out any old data that may reside in demo and APT directories.
        Setup the actual demo environment, and begin creating jobs. Set class status to 1, running.
        :return: Return startup string for web representation
        :rtype: str
        """
        # create exit directories if needed
        if not os.path.exists(self.exit_dir):
            os.makedirs(self.exit_dir)
        if not os.path.exists(self.jif_data):
            os.makedirs(self.jif_data)
        # clean up any outstanding exit data
        files = os.listdir(self.exit_dir)
        logger.demo('--Demo Startup--')
        for file in files:
            os.remove(self.exit_dir + '/' + file)
        logger.demo('Exit directory cleaned up.')
        self.first_run = 0
        logger.demo('Demo Status == 1')
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'message', 'value': 'Running'}))
            client.write_message(json.dumps({'id': 'td', 'value': 'Running'}))
        self.demo_status = 1
        for k in self.active_targets:
            self.create_job(k)
            logger.demo('Creating initial job for target: {}'.format(k.upper()))
        logger.debug('Demo Initialized.')
        return 'Demo initialization and startup complete.'

    def stop_demo(self):
        """
        Clear active job dict and reprint list, reset exit data to a blank directory, set demo status to 0, Stopped.
        :return: Shutdown string for web display.
        :rtype: str
        """
        logger.demo('--Demo Shutdown Initiated--')
        logger.demo('Setting demo status to 0, stopping demo.')
        self.demo_status = 0

        for k in self.all_targets:
            getattr(self, k)['jobid'] = []
            
        self.active_jobs = {}
        self.reprinting_jobs = []
        
        # Clear the worker queues
        self.data_controller.clear_queues()

        # clean up exit data
        files = os.listdir(self.exit_dir)
        logger.demo('Cleaning exit directory.')

        for file in files:
            os.remove(self.exit_dir + '/' + file)

        files = os.listdir(self.proc_dir)
        logger.demo('Cleaning WIP directory.')

        for file in files:
            os.remove(self.proc_dir + '/' + file)

        logger.demo('Resetting demo state')
        self.first_run = 1
        for client in self.clients.values():
            client.write_message(json.dumps({'id': 'message', 'value': 'Stopped'}))
            client.write_message(json.dumps({'id': 'td', 'value': 'Stopped'}))
        logger.demo('--Demo Shutdown Complete--')

        return 'Demo shut down complete.'

    def new_job(self, data):
        """
        When a job is received and added into APT Server it will send a socket request to the socket server.
        This will contain a json payload, indicating instructions, and jobid.
        We then parse the request, and copy appropriate job processing data to the target ICD folder.
        :param data: 
        data[0] == APT Result, Accepted meaning job added and ready, Failed meaning the job was not loaded
        for some reason. Accepted jobs have processing details copied to appropriate ICD folder. Failed jobs get sent to
        completion for a new job generation.
        data[1] == Jobid for the target job.
        :type data: list[str, int] 
        :return: None
        :rtype: None
        """
        jobid = data[1]
        not_found = False

        if data[0] == 'Accepted':
            try:
                icd = self.active_jobs[jobid][0]
                logger.io('--New Job--')
                logger.io('Job {} accepted by APT, sending data.'.format(icd))
                self.data_controller.new_data(jobid, icd)
            except KeyError:
                logger.io('Job not found...')
                not_found = True
        if data[0] == 'Failed':
            logger.io('--New Job--')
            logger.io('JIF for Job {} failed to load into APT. Cycle to the next.'.format(jobid))
            self.complete_job(['Complete', jobid])

        if not_found:
            logger.error('--New Job--')
            logger.error('Job {} was not found in an ICD, could not complete copy.'.format(jobid))

    def proc_phase(self, data):
        """
        When a multi-step job is detected in APT, and transitions from Print -> Insertion it will trigger a socket
        connection sending a payload indicating a processing change has occurred. This will initate a transfer of 
        job state from origin to TD for second step processing. If the TD target has few jobs, and the origin 
        has 1 or no jobs, generate a new job for the origin as well.
        :param data: data[0] == String message of Proc, data[1] == Jobid for target job.
        :type data: list[str, int]
        :return: None
        :rtype: None
        """
        jobid = data[1]
        status = int(data[2])

        if status in (1026, 1030) and jobid in self.active_jobs.keys():
            icd = self.active_jobs[jobid][0]
            origin = self.active_jobs[jobid][1]
            if getattr(self, icd)['multi_step'] == 1:

                if icd.lower() != 'td' and jobid not in self.td['jobid']:
                    logger.io('Multi process change to insert - removing {}'.format(jobid))
                    self.td['jobid'].append(jobid)
                    try:
                        getattr(self, icd)['jobid'].remove(jobid)
                    except ValueError:
                        pass

                    logger.io('Sending data to TD from multi-step.')
                    self.data_controller.new_data(jobid, 'td')
                    logger.io('Cleaning previous data.')

                    if getattr(self, icd)['piece_or_sheet'].lower() == 'sheet':
                        try:
                            files = [f for f in os.listdir(self.exit_dir) if 'sheet' in f if jobid in f]
                            for file in files:
                                os.remove(os.path.join(self.exit_dir, file))
                        except FileNotFoundError:
                            pass
                    if len(getattr(self, icd)['jobid']) <= 1 and len(self.td['jobid']) <= 2:
                        self.create_job(origin)
                    self.active_jobs[jobid][0] = self.td['origin']

    def reprint_job(self, data):
        """
        When APT sends a reprint request, it will trigger a socket connection with payload data indicating a specific
        job requires reprinting. This will initiate a transfer of the job from an ICD to one of the 3 reprint target
        ICD devices. We will also move the job into a reprint_jobs list as well to track active reprints.
        We will select the reprint ICD station from a first available loop.
        :param data: data[0] == String of either Reprint or Complete. Reprint continues, while Complete gets shipped to
        self.complete_job(data).
        data[1] == Jobid
        :type data: list[str, int]
        :return: None
        :rtype: None
        """
        jobid = data[1]

        if data[0] == 'Complete':
            logger.io('Complete call passing to completion {}'.format(jobid))
            self.complete_job(data)
        else:
            logger.io('Reprint Call incoming data {} and active jobs {} '
                      'listed reprinting jobs {}'.format(jobid, self.active_jobs.keys(), self.reprinting_jobs))
            if jobid in self.active_jobs.keys() and jobid not in self.reprinting_jobs:
                origin = self.active_jobs[jobid][1]
                icd = self.active_jobs[jobid][0]
                if getattr(self, icd)['multi_step'] == 1:
                    logger.io('Multi-step transition not yet complete!')
                else:
                    try:
                        getattr(self, icd)['jobid'].remove(jobid)
                    except ValueError:
                        pass
                    if jobid[:2] in ['A1', 'A2', 'A3'] and len(getattr(self, origin)['jobid']) <= 1:
                        if getattr(self, origin)['multi_step'] == 1 and len(self.td['jobid']) <= 1:
                            self.create_job(origin)
                        if getattr(self, origin)['multi_step'] == 0:
                            self.create_job(origin)
                    logger.io('Copying {} to reprint directory'.format(jobid))
                    done = False
                    reprint_target = None
                    while not done:
                        for station in self.reprint_pool:
                            if not done:
                                for dirpath, dirnames, files in os.walk(getattr(self, station)['path']):
                                        if not files:
                                            reprint_target = station
                                            done = True
                                            break
                                        else:
                                            pass
                            else:
                                break

                    getattr(self, reprint_target)['jobid'].append(jobid)

                    reprints = None

                    with open(os.path.join(self.reprint_folder, '{}.1.txt'.format(jobid)), 'r') as fp:
                        reprints = fp.read()

                    reprint_generated = jif_assembler.gen_reprints(jobid, getattr(self, origin), reprints)

                    if reprint_generated:
                        self.data_controller.new_data(jobid, reprint_target)
                        self.active_jobs[jobid][0] = reprint_target
                        self.reprinting_jobs.append(jobid)
                    else:
                        logger.debug('Reprint went seriously wrong.')

    def complete_job(self, data):
        """
        When APT registers a completed job it will send a socket connection to our program indication completion. This
        will trigger us to create a new job, if it is not an A4 prefix (TD) job, or if the origin has 1 or less jobs
        it is currently working on.
        We will remove the jobid from the active_jobs dict, and append it to the completed jobs list. If it was also in
        the reprint list, we will remove it from there as well.
        :param data: data[0] == String of Complete, data[1] == Jobid
        :type data: list[str, int]
        :return: None
        :rtype: None
        """
        jobid = data[1]
        prefix = jobid[:2]
        if jobid in self.active_jobs.keys() and jobid not in self.completed_jobs:
            origin = self.active_jobs[jobid][1]
            icd = self.active_jobs[jobid][0]

            files = [os.path.join(self.exit_dir, i) for i in os.listdir(self.exit_dir) if jobid in i]

            logger.io('--Job Completed--')
            logger.io('JobID {}'.format(jobid))
            logger.io('Cleaning old job data.')

            for file in files:
                if os.path.exists(file):
                    os.remove(file)

            self.completed_jobs.append(jobid)
            if jobid in self.reprinting_jobs:
                self.reprinting_jobs.remove(jobid)
            try:
                getattr(self, icd)['jobid'].remove(jobid)
            except ValueError:
                pass
            if len(getattr(self, origin)['jobid']) <= 1:
                if prefix == 'A4':
                    logger.io('Initial TD Job Completed. {}'.format(jobid))
                else:
                    self.create_job(origin)
            del self.active_jobs[jobid]
        else:
            logger.io('Completed job call, but job is already listed as complete {}'.format(jobid))
