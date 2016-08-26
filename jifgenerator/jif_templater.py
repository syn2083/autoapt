from os import path
import datetime
from django.shortcuts import get_object_or_404
from ..models import JIFTemplate
from automated_APTDemo import logging_setup

logger = logging_setup.init_logging()

__author__ = 'venom'


class Template(object):
    def __init__(self):
        jif = get_object_or_404(JIFTemplate, pk=1)
        t = datetime.datetime.now() - datetime.timedelta(hours=3)
        self.initial_seed = '0000001'
        self.site_prefix = None
        self.job_id = '0000001'
        self.template_name = jif.template_name
        self.piece_range = jif.piece_range
        self.sheet_range = '1, 8'
        self.num_jifs = 1
        self.account = jif.account_id
        self.job_name = jif.job_name
        self.job_type = jif.job_type
        self.jobclass = jif.job_class
        self.job_number = jif.job_number
        self.envelope_id = jif.envelope_id
        self.stock_id = jif.stock_id
        self.stock_type = jif.stock_type
        self.prod_loc = jif.production_location
        self.product_name = jif.product_name
        self.userinfo1 = jif.user_info_1
        self.userinfo2 = jif.user_info_2
        self.userinfo3 = jif.user_info_3
        self.userinfo4 = jif.user_info_4
        self.userinfo5 = jif.user_info_5
        self.contact_email = jif.contact_email
        self.imp_mult = '1,2'
        self.shift_1_operators = jif.shift_1_operators
        self.shift_2_operators = jif.shift_2_operators
        self.shift_3_operators = jif.shift_3_operators
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
