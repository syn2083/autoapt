import os
import shutil
from collections import deque
from logging_setup import init_logging
from jifgenerator import jif_assembler

"""
This is the Demo Controller Brain.
"""
logger = init_logging()


class DemoController:
    def __init__(self, dconf, jconf):
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
        self.lock = None
        self.dispatcher = None
        self.observers = []
        self.socket_server = None
        self.command_queue = deque()
        self.proc_queue = deque()
        self.active_jobs = {}
        self.completed_jobs = []
        self.reprinting_jobs = []
        self.exit_data = dconf[1]['DemoDirs']['exit_data']
        self.jif_data = dconf[1]['DemoDirs']['jif_data']
        self.jif_folder = dconf[1]['APTDirs']['JDF']
        self.first_run = 1
        self.target_dirs = {k: dconf[0][k]['path'] for k in dconf[0].keys()}
        self.jifconfig = jconf
        self.democonf = dconf

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
        if not os.path.exists(self.democonf[1]['DemoDirs']['exit_data']):
            os.makedirs(self.democonf[1]['DemoDirs']['exit_data'])
        if not os.path.exists(self.democonf[1]['DemoDirs']['jif_data']):
            os.makedirs(self.democonf[1]['DemoDirs']['jif_data'])
        # clean up any outstanding exit data
        files = os.listdir(self.exit_data)
        logger.demo('--Demo Startup--')
        for file in files:
            os.remove(self.exit_data + '/' + file)
        logger.demo('Exit directory cleaned up.')
        self.first_run = 0
        logger.demo('Demo Status == 1')
        self.demo_status = 1
        logger.debug(self.active_targets)
        for k in self.active_targets:
            logger.debug('Target {}'.format(k))
            jifconstruct = jif_assembler.JIFBuilder(k, self.jif_folder, self.democonf, self.jifconfig)
            getattr(self, k)['jobid'].append(jifconstruct.gen_jifs())
            self.active_jobs[getattr(self, k)['jobid'][-1]] = [k, k]
            logger.demo('Creating initial job for target: {}'.format(k.upper()))
        logger.debug('Demo Initialized.')
        return 'Demo initialization and startup complete.'

    def stop_demo(self):
        """
        Clear active job dict and reprint list, reset exit data to a blank directory, set demo status to 0, stopped.
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

        # clean up exit data
        files = os.listdir(self.exit_data)
        logger.demo('Cleaning exit directory.')

        for file in files:
            os.remove(self.exit_data + '/' + file)

        logger.demo('Resetting demo state')
        self.first_run = 1
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
                exit_dir = self.exit_data
                logger.io('--New Job--')
                logger.io('Job {} accepted by APT, sending data.'.format(icd))
                if getattr(self, icd)['piece_or_sheet'].lower() == 'piece':
                    data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
                    target = os.path.join(getattr(self, icd)['path'], 'piece_{}.txt'.format(jobid))
                else:
                    data_file = os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid))
                    target = os.path.join(getattr(self, icd)['path'], 'sheet_{}.txt'.format(jobid))
                shutil.copyfile(data_file, target)
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

        if jobid in self.active_jobs.keys():
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

                    exit_dir = self.exit_data
                    data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
                    file_out = os.path.join(self.td['path'], 'piece_{}.txt'.format(jobid))

                    logger.io('Sending data to TD from multi-step.')
                    shutil.copyfile(data_file, file_out)
                    logger.io('Cleaning previous data.')

                    if getattr(self, icd)['piece_or_sheet'].lower() == 'sheet':
                        try:
                            os.remove(os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid)))
                        except FileNotFoundError:
                            pass
                    if len(getattr(self, icd)['jobid']) <= 1 and len(self.td['jobid']) <= 2:
                        gen = jif_assembler.JIFBuilder(origin, self.jif_folder, self.democonf, self.jifconfig)
                        logger.io('Creating {} JIF/Exit Data'.format(origin.upper()))
                        new_job = gen.gen_jifs()
                        getattr(self, origin)['jobid'].append(new_job)
                        self.active_jobs[new_job] = [origin, origin]
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
                        if (getattr(self, origin)['multi_step'] == 1 and self.td['jobid'] >= 2) or getattr(self, origin)['multi_step'] == 0:
                            gen = jif_assembler.JIFBuilder(origin, self.jif_folder, self.democonf, self.jifconfig)
                            logger.io('Creating {} JIF/Exit Data'.format(icd.upper()))
                            new_job = gen.gen_jifs()
                            getattr(self, origin)['jobid'].append(new_job)
                            self.active_jobs[new_job] = [origin, origin]
                    exit_dir = self.exit_data
                    data_file = os.path.join(exit_dir, 'reprint_{}.txt'.format(jobid))
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
                    send_to = os.path.join(getattr(self, reprint_target)['path'], 'reprint_{}.txt'.format(jobid))
                    getattr(self, reprint_target)['jobid'].append(jobid)
                    self.active_jobs[jobid][0] = reprint_target
                    self.reprinting_jobs.append(jobid)
                    shutil.copyfile(data_file, send_to)

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

            exit_dir = self.exit_data
            files = [os.path.join(exit_dir, 'piece_{}.txt'.format(jobid)),
                     os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid)),
                     os.path.join(exit_dir, 'reprint_{}.txt'.format(jobid))]

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
                    gen = jif_assembler.JIFBuilder(origin, self.jif_folder, self.democonf, self.jifconfig)
                    logger.io('Creating {} JIF/Exit Data'.format(origin.upper()))
                    new_job = gen.gen_jifs()
                    getattr(self, origin)['jobid'].append(new_job)
                    self.active_jobs[new_job] = [origin, origin]
            del self.active_jobs[jobid]
        else:
            logger.io('Completed job call, but job is already listed as complete {}'.format(jobid))
