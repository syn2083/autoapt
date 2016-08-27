import os
import shutil
import threading
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

    def remove_job(self, idc=None, jobid=None):
        pass

    def add_job(self, jobid=None):
        pass

    def multi_job(self, jobid=None):
        if not jobid:
            logger.debug('Multi-job processor called with no jobid.')
        if not self.multi_step:
            pass
        if jobid in self.icd_1:
            if self.td:
                logger.debug('Multi-job passing to TD but it is busy.')
                # will try to add, and let next step handle this situation
                self.td.append(jobid)
            else:
                self.td.append(jobid)

    def reprint_request(self, jobid=None):
        pass

    def start_demo(self):
        # clean up any outstanding exit data
        files = os.listdir(self.exit_data)
        logger.demo('--Demo Startup--')
        for file in files:
            os.remove(self.exit_data + '/' + file)
        logger.demo('Exit directory cleaned up.')
        self.first_run = 0
        logger.demo('Demo Status == 1')
        self.demo_status = 1
        for k in self.active_targets:
            jifconstruct = jif_assembler.JIFBuilder(k, self.jif_folder, getattr(self, k)['multi_step'],
                                                    self.democonf, self.jifconfig)

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
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers = []
        self.dispatcher.stop()
        self.dispatcher.join()
        self.dispatcher = None
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

                    logger.iohandler('--New Job--\n Copying data for job {}.'.format(jobid))
                    if getattr(self, k)['piece_sheet'].lower() == 'piece':
                        data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
                        target = os.path.join(getattr(self, k)['path'], 'piece_{}.txt'.format(jobid))
                    else:
                        data_file = os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid))
                        target = os.path.join(getattr(self, k)['path'], 'sheet_{}.txt'.format(jobid))
                    shutil.copyfile(data_file, target)
                    not_found = False
            if data[0] == 'Failed':
                logger.iohandler('--New Job--\n JIF for Job {} failed to load into APT.'.format(jobid))
                self.complete_job(['Complete', jobid])

        if not_found:
            logger.error('--New Job--\n Job {} was not found in an ICD, could not complete copy.'.format(jobid))

    def proc_phase(self, data):
        jobid = data[1]
        logger.debug('Multi-step input id {} icd_1 id {}'.format(jobid, self.icd_1))

        if jobid in self.icd_1:
            logger.debug('Multi process change from print to insert - removing {}'.format(jobid))
            if self.td:
                logger.debug('Multi process collision detected in TD.')
            self.td.append(self.icd_1.pop())
            exit_dir = self.exit_data
            data_file = os.path.join(exit_dir, 'piece_{}.txt'.format(jobid))
            target = os.path.join(self.target_dirs['td'], 'piece_{}.txt'.format(jobid))
            shutil.copyfile(data_file, target)
            logger.debug('Cleaning print data.')
            os.remove(os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid)))

    def reprint_job(self, data):
        jobid = data[1]

        if data[0] == 'Complete':
            self.complete_job(data)
        else:
            if jobid in self.icd_1:
                logger.debug('ICD1 transition not complete - reprint call {}'.format(jobid))

            else:
                if jobid in self.icd_2:
                    logger.debug('Transferring ICD2 reprint {}'.format(jobid))
                    self.icd_4.append(self.icd_2.pop())
                if jobid in self.icd_3:
                    logger.debug('Transferring ICD3 reprint {}'.format(jobid))
                    self.icd_4.append(self.icd_3.pop())
                if jobid in self.td:
                    logger.debug('Transferring TD reprint {}'.format(jobid))
                    self.icd_4.append(self.td.pop())
                exit_dir = self.exit_data
                data_file = os.path.join(exit_dir, 'reprint_{}.txt'.format(jobid))
                logger.debug('Copying {} to reprint directory'.format(jobid))
                done = None
                while True:
                    if not done:
                        for dirpath, dirnames, files in os.walk(self.target_dirs['icd_4']):
                            if not done:
                                if not files:
                                    target = os.path.join(self.target_dirs['icd_4'], 'reprint_{}.txt'.format(jobid))
                                    shutil.copyfile(data_file, target)
                                    done = True
                                    break
                                else:
                                    pass
                        for dirpath, dirnames, files in os.walk(self.target_dirs['icd_5']):
                            if not done:
                                if not files:
                                    target = os.path.join(self.target_dirs['icd_5'], 'reprint_{}.txt'.format(jobid))
                                    shutil.copyfile(data_file, target)
                                    done = True
                                    break
                                else:
                                    pass
                        for dirpath, dirnames, files in os.walk(self.target_dirs['icd_6']):
                            if not done:
                                if not files:
                                    target = os.path.join(self.target_dirs['icd_6'], 'reprint_{}.txt'.format(jobid))
                                    shutil.copyfile(data_file, target)
                                    done = True
                                    break
                                else:
                                    pass
                    else:
                        break

    def complete_job(self, data):
        jobid = data[1]

        exit_dir = self.exit_data
        files = [os.path.join(exit_dir, 'piece_{}.txt'.format(jobid)),
                 os.path.join(exit_dir, 'sheet_{}.txt'.format(jobid)),
                 os.path.join(exit_dir, 'reprint_{}.txt'.format(jobid))]

        logger.debug('Cleaning old job data.')

        self.completed_jobs.append(jobid)

        for file in files:
            if os.path.exists(file):
                os.remove(file)

        if jobid in self.icd_4:
            self.icd_4.remove(jobid)

        if 'A4' in jobid:
            if jobid in self.td:
                self.td.remove(jobid)
                logger.debug('Initial TD job completed: {}'.format(self.td.pop()))

        if 'A1' in jobid:
            self.td.remove(jobid)
            icd_1 = jif_assembler.JIFBuilder('icd_1', self.jif_folder, 1)
            logger.debug('Creating ICD 1 JIF/Exit Data')
            self.icd_1.append(icd_1.gen_jifs())
        if 'A2' in jobid:
            icd_2 = jif_assembler.JIFBuilder('icd_2', self.jif_folder, None)
            logger.debug('Creating ICD 2 JIF/Exit Data')
            self.icd_2.append(icd_2.gen_jifs())
        if 'A3' in jobid:
            icd_3 = jif_assembler.JIFBuilder('icd_3', self.jif_folder, None)
            logger.debug('Creating ICD 3 JIF/Exit Data')
            self.icd_3.append(icd_3.gen_jifs())
        self.completed_jobs.append(jobid)

    def command_init(self):
        pass

