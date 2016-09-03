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
        self.completed_jobs = []
        self.exit_data = dconf[1]['DemoDirs']['exit_data']
        self.jif_data = dconf[1]['DemoDirs']['jif_data']
        self.jif_folder = dconf[1]['APTDirs']['JDF']
        self.first_run = 1
        self.target_dirs = {k: dconf[0][k]['path'] for k in dconf[0].keys()}
        self.jifconfig = jconf
        self.democonf = dconf

    def __repr__(self):
        if self.demo_status == 0:
            return 'Not Running'
        if self.demo_status == 1:
            return 'Running'
        if self.demo_status == 2:
            return 'Paused'

    def reset_seed(self):
        seed_loc = os.path.join(os.getcwd(), 'jifgenerator/job_seed.txt')
        logger.demo('Resetting job seed to 1')
        with open(seed_loc, 'w') as fp:
            fp.write('1')
        return 'Reset job seed to 1'

    def start_demo(self):
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
            logger.demo('Creating initial job for target: {}'.format(k.upper()))
        logger.debug('Demo Initialized.')
        return 'Demo initialization and startup complete.'

    def stop_demo(self):
        logger.demo('--Demo Shutdown Initiated--')
        logger.demo('Setting demo status to 0, stopping demo.')
        self.demo_status = 0

        for k in self.all_targets:
            getattr(self, k)['jobid'] = []

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
        jobid = data[1]
        not_found = True

        for k in self.active_targets:
            if data[0] == 'Accepted':
                if jobid in getattr(self, k)['jobid']:
                    exit_dir = self.exit_data

                    logger.io('--New Job--')
                    logger.io('Creating new job for target {}'.format(k))
                    if getattr(self, k)['piece_or_sheet'].lower() == 'piece':
                        data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
                        target = os.path.join(getattr(self, k)['path'], 'piece_{}.txt'.format(jobid))
                    else:
                        data_file = os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid))
                        target = os.path.join(getattr(self, k)['path'], 'sheet_{}.txt'.format(jobid))
                    shutil.copyfile(data_file, target)
                    not_found = False
            if data[0] == 'Failed':
                logger.io('--New Job--')
                logger.io('JIF for Job {} failed to load into APT.'.format(jobid))
                self.complete_job(['Complete', jobid])

        if not_found:
            logger.error('--New Job--')
            logger.error('Job {} was not found in an ICD, could not complete copy.'.format(jobid))

    def proc_phase(self, data):
        jobid = data[1]

        for target in self.active_targets:
            if getattr(self, target)['multi_step'] == 1:
                if target != 'td':
                    if jobid in getattr(self, target)['jobid']:
                        logger.io('Multi process change to insert - removing {}'.format(jobid))
                        self.td['jobid'].append(jobid)
                        getattr(self, target)['jobid'].remove(jobid)
                        exit_dir = self.exit_data
                        data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
                        file_out = os.path.join(self.td['path'], 'piece_{}.txt'.format(jobid))
                        logger.io('Sending data to TD from multi-step.')
                        shutil.copyfile(data_file, file_out)
                        logger.io('Cleaning previous data.')
                        if getattr(self, target)['piece_or_sheet'].lower() == 'sheet':
                            os.remove(os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid)))
                        gen = jif_assembler.JIFBuilder(getattr(self, target)['origin'], self.jif_folder,
                                                       self.democonf, self.jifconfig)
                        logger.io('Creating {} JIF/Exit Data'.format(target.upper()))
                        getattr(self, target)['jobid'].append(gen.gen_jifs())

    def reprint_job(self, data):
        jobid = data[1]

        if data[0] == 'Complete':
            self.complete_job(data)
        else:
            for target in self.active_targets:
                if jobid in getattr(self, target)['jobid']:
                    if getattr(self, target)['multi_step'] == 1:
                        logger.io('Multi-step transition not yet complete!')
                    else:
                        if jobid[:2] != 'A4':
                            getattr(self, target)['jobid'].remove(jobid)
                            gen = jif_assembler.JIFBuilder(getattr(self, target)['origin'], self.jif_folder,
                                                           self.democonf, self.jifconfig)
                            logger.io('Creating {} JIF/Exit Data'.format(target.upper()))
                            getattr(self, target)['jobid'].append(gen.gen_jifs())

                        exit_dir = self.exit_data
                        data_file = os.path.join(exit_dir, 'reprint_{}.txt'.format(jobid))
                        logger.io('Copying {} to reprint directory'.format(jobid))
                        done = False
                        while not done:
                            for station in self.reprint_pool:
                                if not done:
                                    for dirpath, dirnames, files in os.walk(getattr(self, station)['path']):
                                            if not files:
                                                send_to = os.path.join(getattr(self, station)['path'],
                                                                       'reprint_{}.txt'.format(jobid))
                                                getattr(self, station)['jobid'].append(jobid)
                                                shutil.copyfile(data_file, send_to)
                                                done = True
                                                break
                                            else:
                                                pass
                                else:
                                    break

    def complete_job(self, data):
        jobid = data[1]
        prefix = jobid[:2]
        origin = None

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

        # find origin
        for machine in self.active_targets:
            if jobid[:2] == getattr(self, machine)['site_prefix'][:2]:
                origin = machine

        for target in self.all_targets:
            if jobid in getattr(self, target)['jobid']:
                icd = getattr(self, target)
                try:
                    self.completed_jobs.append(jobid)
                    icd['jobid'].remove(jobid)
                    if origin in self.active_targets:
                        if prefix == 'A4':
                            logger.io('Initial TD Job Completed. {}'.format(jobid))
                        else:
                            gen = jif_assembler.JIFBuilder(origin, self.jif_folder, self.democonf, self.jifconfig)
                            logger.io('Creating {} JIF/Exit Data'.format(origin.upper()))
                            getattr(self, origin)['jobid'].append(gen.gen_jifs())
                except AttributeError:
                    logger.error('Attempted to remove {} from {}, non existent jobid'.format(jobid, target))
                    pass
