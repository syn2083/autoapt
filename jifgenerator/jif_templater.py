from os import path
import datetime
from logging_setup import init_logging

logger = init_logging()

__author__ = 'venom'


class Template(object):
    def __init__(self):
        t = datetime.datetime.now() - datetime.timedelta(hours=3)
        self.initial_seed = '0000001'
        self.site_prefix = None
        self.job_id = '0000001'
        self.temp_name = None
        self.prange = None
        self.srange = None
        self.num_jifs = None
        self.actid = None
        self.jname = None
        self.jtype = None
        self.jclass = None
        self.jnum = None
        self.envid = None
        self.stockid = None
        self.stocktype = None
        self.prodloc = None
        self.prodname = None
        self.ui1 = None
        self.ui2 = None
        self.ui3 = None
        self.ui4 = None
        self.ui5 = None
        self.cemail = None
        self.imp_mult = '1,2'
        self.shift1 = None
        self.shift2 = None
        self.shift3 = None
        self.creation = [str(t), t]
        self.deadline = ''
        self.current_jobid = None
        self.current_piececount = None
        self.damages = None
        self.generated_jobs = None
        self.curr_time = None
        self.curr_exit_time = None
        self.damage_count = 0
        self.current_bad = 0

    def id_to_int(self):
        try:
            return int(self.job_id)
        except ValueError:
            return None

    def id_to_str(self, input_id):
        try:
            return str(input_id).zfill(7)
        except:
            return None

    def jobid_loader(self):
        logger.debug('JobID Loader called')
        local_path = path.dirname(path.abspath(__file__))
        logger.debug('Data path = {}'.format(local_path))
        seeder = path.join(local_path, "job_seed.txt")
        if not path.isfile(seeder):
            with open(seeder, 'w') as fp:
                fp.write('0000001')
            fp.close()
            self.current_jobid = 1
            logger.debug('Jobid set to 1 called inside non found seed file.')
        else:
            with open(seeder, 'r') as fp:
                self.current_jobid = int(fp.read())
                logger.debug('Jobid = {}'.format(self.current_jobid))
            fp.close()

    def jobid_saver(self):
        local_path = path.dirname(path.abspath(__file__))
        seeder = path.join(local_path, "job_seed.txt")
        if not path.isfile(seeder):
            with open(seeder, 'w') as fp:
                fp.write('0000001')
            fp.close()
        else:
            with open(seeder, 'w') as fp:
                fp.write(str(self.current_jobid))
            fp.close()

    def add_seconds(self, in_time, secs):
        return in_time + datetime.timedelta(seconds=secs)
