import datetime
import os
import shutil
import copy
from random import choice, randint, sample, random
from os import path
from .prog_utilities import folder_construct, str_to_list, find_shift
from logging_setup import init_logging

__author__ = 'venom'

"""This module handles utilizing a JIF Template to produce output. It has builtin assemblers for the
job ticket and piece manifesting, feed scan data, and exit scan data where appropriate. The output data will be placed
in a local directory in the following format:
Output
-TemplateName
--feed_data
--exit_data
--jif_output"""

logger = init_logging()


class JIFBuilder:
    def __init__(self, icd_target, jdf_folder, dconf, jconf):
        for k in jconf[0]['JIF'].keys():
            setattr(self, k, jconf[0]['JIF'][k])
        for k in jconf[0]['OPTS'].keys():
            setattr(self, k, jconf[0]['OPTS'][k])
        for k in dconf[0][icd_target].keys():
            setattr(self, k, dconf[0][icd_target][k])
        self.reprinters = {}
        for t in dconf[2]['reprint_pool']:
            self.reprinters[t] = {'shift1': dconf[0][t]['shift1'], 'shift2': dconf[0][t]['shift2'],
                                  'shift3': dconf[0][t]['shift3']}
        self.out = jdf_folder
        self.target = icd_target
        if self.speed:
            self.speed = (self.speed // 60) // 60
            if self.speed == 0:
                self.speed = 1
        self.r_speed = 2
        t = datetime.datetime.now() - datetime.timedelta(hours=3)
        self.initial_seed = '0000001'
        self.job_id = '0000001'
        self.imp_mult = '1,2'
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

    def piece_builder(self, piece_id):
        plist = []
        bstr = "\n"

        plist.append("   <Piece>")
        plist.append("    <ID>{pieceid}</ID>".format(pieceid=str(piece_id).zfill(6)))
        rlist = [i.strip() for i in self.srange.split(',')]
        sheet_count = randint(int(rlist[0]), int(rlist[1]))
        plist.append("    <TotalSheets>{totals}</TotalSheets>".format(totals=str(sheet_count)))
        plist.append("   </Piece>")
        return [bstr.join(plist), sheet_count]

    def gen_jifs(self):
        bstr = "\n"
        make_damages = 0
        pcomp_to_use = choice(['1', '2'])
        pcomp = '{}'.format(pcomp_to_use)

        self.jobid_loader()
        logger.jifgen('Starting to build JIF {}{}.'.format(self.site_prefix, self.id_to_str(self.current_jobid)))
        conv_dict = {'jtype': [self.jtype, None],
                     'jname': [self.jname, None],
                     'jnum': [self.jnum, None],
                     'prodname': [self.prodname, None],
                     'prodloc': [self.prodloc, None],
                     'envid': [self.envid, None],
                     'stockid': [self.stockid, None],
                     'stocktype': [self.stocktype, None],
                     'actid': [self.actid, None],
                     'jclass': [self.jclass, None],
                     'imp_mult': [self.imp_mult, None],
                     'ui1': [self.ui1, None],
                     'ui2': [self.ui2, None],
                     'ui3': [self.ui3, None],
                     'ui4': [self.ui4, None],
                     'ui5': [self.ui5, None],
                     'shift_1_ops': [self.shift1, None],
                     'shift_2_ops': [self.shift2, None],
                     'shift_3_ops': [self.shift3, None]}

        for k, v in conv_dict.items():
            v[1] = str_to_list(v[0])

        if 20 >= randint(1, 100):
            self.damage_count = 1
            self.damages = 1

        for i in range(0, self.num_jifs):

            if not self.generated_jobs:
                self.generated_jobs = 0
            if self.damages:
                if self.current_bad <= self.damage_count:
                    make_damages = 1
                    self.current_bad += 1
            jif_strings = []
            sheet_list = []
            jif_strings.append("""<?xml version="1.0" encoding="UTF-8"?>\n <JobTicket>\n <Version>2.2</Version>""")
            jif_strings.append(" <JobID>{pref}{jobid}</JobID>".format(pref=self.site_prefix,
                                                                      jobid=self.id_to_str(self.current_jobid)))
            jif_strings.append(" <JobType>{}</JobType>".format(choice(conv_dict['jtype'][1])))
            jif_strings.append(" <JobName>{}</JobName>".format(choice(conv_dict['jname'][1])))
            jif_strings.append(" <JobNumber>{}{}</JobNumber>".format(choice(conv_dict['jnum'][1]), randint(1000, 9999)))
            jif_strings.append(" <ProductName>{}</ProductName>".format(choice(conv_dict['prodname'][1])))
            jif_strings.append(" <AccountID>{}</AccountID>".format(choice(conv_dict['actid'][1])))
            jif_strings.append(" <StartSequence>000001</StartSequence>")
            count = [i.strip() for i in self.prange.split(',')]
            self.current_piececount = randint(int(count[0]), int(count[1]))
            jif_strings.append(" <EndSequence>{}</EndSequence>".format(str(self.current_piececount).zfill(6)))
            jif_strings.append(" <PieceCount>{}</PieceCount>".format(str(self.current_piececount)))
            jif_strings.append(" <CreationDate>{}</CreationDate>".format(self.creation[0]))
            if 9 >= randint(1, 100):
                if self.multi_step == 1:
                    jif_strings.append(" <JobDeadLine>{}</JobDeadLine>".format(self.creation[1] +
                                                                               datetime.timedelta(hours=1, minutes=4)))
                else:
                    jif_strings.append(" <JobDeadLine>{}</JobDeadLine>".format(self.creation[1] +
                                                                               datetime.timedelta(minutes=4)))
            else:
                jif_strings.append(" <JobDeadLine/>")
            jif_strings.append(" <PrintMode>1</PrintMode>")
            pcomp = choice(['1', '2'])
            jif_strings.append(" <PageComposition>{}</PageComposition>".format(pcomp))
            jif_strings.append(" <ProcessingPhases>{}</ProcessingPhases>".format(self.proc_phase))
            jif_strings.append(" <EndProcess>{}</EndProcess>".format(self.end_phase))
            jif_strings.append(" <ProductionLocation>{}</ProductionLocation>".format(choice(conv_dict['prodloc'][1])))
            jif_strings.append(" <Class>{}</Class>".format(choice(conv_dict['jclass'][1])))
            jif_strings.append(" <EnvelopeID>{}</EnvelopeID>".format(choice(conv_dict['envid'][1])))
            jif_strings.append(" <StockID>{}</StockID>".format(choice(conv_dict['stockid'][1])))
            jif_strings.append(" <StockType>{}</StockType>".format(choice(conv_dict['stocktype'][1])))
            if '30' in self.end_phase:
                jif_strings.append(" <UserInfo1>None</UserInfo1>")
                jif_strings.append(" <UserInfo2>{}</UserInfo2>".format(choice(conv_dict['ui2'][1])))
            else:
                jif_strings.append(" <UserInfo1>{}</UserInfo1>".format(choice(conv_dict['ui1'][1])))
                jif_strings.append(" <UserInfo2>None</UserInfo2>")
            jif_strings.append(" <UserInfo3>{}{}-{}</UserInfo3>".format(choice(conv_dict['ui3'][1]),
                                                                        randint(100, 999), randint(1000, 9999)))
            jif_strings.append(" <UserInfo4>{}</UserInfo4>".format(choice(conv_dict['ui4'][1])))
            jif_strings.append(" <UserInfo5>{}</UserInfo5>".format(choice(conv_dict['ui5'][1])))
            # jif_strings.append("  <JobManifest>")
            logger.debug('Building Sheets.')
            for t in range(1, self.current_piececount + 1):
                result = self.piece_builder(t)
                # jif_strings.append(result[0])
                sheet_list.append(result[1])
            # jif_strings.append("  </JobManifest>")
            multi = int(pcomp)
            sheets = 0
            for x in sheet_list:
                sheets += x
            jif_strings.append(" <SheetCount>{}</SheetCount>".format(sheets))
            jif_strings.append(" <PageCount>{}</PageCount>".format(multi * sheets))
            jif_strings.append(" </JobTicket>\n")
            jstr = bstr.join(jif_strings)

            logger.debug('Generating ICD Data.')

            if self.piece_or_sheet.lower() == 'sheet':
                if self.multi_step:
                    if make_damages:
                        sheet_reprints = self.gen_sheet_data(create_damages=1, num_sheets=sheet_list, ops=conv_dict)
                        piece_reprints = self.gen_piece_data(create_damages=1, ops=conv_dict)
                        reprint_set = set()
                        reprint_set.update(sheet_reprints)
                        reprint_set.update(piece_reprints)
                        self.gen_reprints(reprint_set)
                    else:
                        self.gen_sheet_data(create_damages=0, num_sheets=sheet_list, ops=conv_dict)
                        self.gen_piece_data(create_damages=0, ops=conv_dict)
                else:
                    if make_damages:
                        sheet_reprints = self.gen_sheet_data(create_damages=1, num_sheets=sheet_list, ops=conv_dict)
                        self.gen_reprints(sheet_reprints)
                    else:
                        self.gen_sheet_data(create_damages=0, num_sheets=sheet_list, ops=conv_dict)
            if self.piece_or_sheet.lower() == 'piece':
                if make_damages:
                    piece_reprints = self.gen_piece_data(create_damages=1, ops=conv_dict)
                    self.gen_reprints(piece_reprints)
                else:
                    self.gen_piece_data(ops=conv_dict)

            present_jobid = '{}{}'.format(self.site_prefix, str(self.current_jobid).zfill(7))
            self.current_jobid += 1
            self.generated_jobs += 1
            logger.debug('Saving Job Seed')
            self.jobid_saver()
            temp_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output\\aptdemo\\jif_output')
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            filename = path.join(temp_folder, present_jobid + ".jif")
            with open(filename, 'w') as fp:
                fp.write(jstr)
            fp.close()
            logger.debug('Copying JIF to JDF folder.')
            shutil.copyfile(filename, os.path.join(self.out, present_jobid + '.jif'))
            logger.debug('Cleaning temp JIF')
            try:
                os.remove(filename)
            except PermissionError:
                pass
            logger.debug('JIF creation completed. {} has been sent to APT.'.format(present_jobid))
            return present_jobid

    def gen_sheet_data(self, create_damages=None, num_sheets=None, ops=None):
        out_str = "\n"
        out_path = folder_construct()
        sheet_strings = []
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        self.curr_time = self.creation[1]
        sheet_count = 0
        sheet_damage_list = []
        operator = None
        prange = range(1, self.current_piececount + 1)

        if find_shift() == 1:
            operator = choice(ops['shift_1_ops'][1])
        if find_shift() == 2:
            operator = choice(ops['shift_2_ops'][1])
        if find_shift() == 3:
            operator = choice(ops['shift_3_ops'][1])

        if create_damages:
            sheet_damage_list = sample(prange, choice([1, 5, 10, 15, 20, 25]))

        for i in prange:
            for t in range(1, num_sheets[i - 1] + 1):
                if i in sheet_damage_list:
                    sheet_strings.append("{jobid},{pieceid},{cur_sheet},{total_sheet},{time},"
                                         "{result},{op}".format(jobid=job_string,
                                                                pieceid=str(i).zfill(6),
                                                                cur_sheet=str(t).zfill(2),
                                                                total_sheet=str(num_sheets[i - 1]).zfill(2),
                                                                time=self.curr_time,
                                                                result='1',
                                                                op=operator))
                else:
                    sheet_strings.append("{jobid},{pieceid},{cur_sheet},{total_sheet},{time},"
                                         "{result},{op}".format(jobid=job_string,
                                                                pieceid=str(i).zfill(6),
                                                                cur_sheet=str(t).zfill(2),
                                                                total_sheet=str(num_sheets[i - 1]).zfill(2),
                                                                time=self.curr_time,
                                                                result='0',
                                                                op=operator))
                if 'sheet' in self.piece_or_sheet.lower():
                    sheet_count += 1
                    if sheet_count % self.speed == 0:
                        self.curr_time = self.add_seconds(self.curr_time, 1)

        filename = path.join(out_path, "sheet_" + job_string + ".txt")
        logger.debug('Writing Sheet File.')
        with open(filename, 'w') as fp:
            fp.write(out_str.join(sheet_strings) + '\n')
        fp.close()
        self.curr_time = None
        return sheet_damage_list

    def gen_piece_data(self, create_damages=0, ops=None):
        out_str = "\n"
        out_path = folder_construct()
        piece_strings = []
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        damage_list = []
        operator = None
        prange = range(1, self.current_piececount + 1)

        if self.multi_step == 1:
            self.curr_time = self.creation[1] + datetime.timedelta(hours=1)
        else:
            self.curr_time = self.creation[1]

        if find_shift() == 1:
            operator = choice(ops['shift_1_ops'][1])
        if find_shift() == 2:
            operator = choice(ops['shift_2_ops'][1])
        if find_shift() == 3:
            operator = choice(ops['shift_3_ops'][1])

        if create_damages:
            if create_damages:
                damage_list = sample(prange, choice([1, 5, 10, 15, 20, 25]))

        for i in prange:
            if i in damage_list:
                if self.multi_step == 1 or self.target.lower() == 'td':
                    if i == 1:
                        damage_list.remove(1)
                        piece_strings.append("{jobid},{pieceid},{time},{result},{op}".format(jobid=job_string,
                                                                                             pieceid=str(i).zfill(6),
                                                                                             time=self.curr_time,
                                                                                             result='0',
                                                                                             op=operator))
                    elif i == prange[-1]:
                        damage_list.remove(i)
                        piece_strings.append("{jobid},{pieceid},{time},{result},{op}".format(jobid=job_string,
                                                                                             pieceid=str(i).zfill(6),
                                                                                             time=self.curr_time,
                                                                                             result='0',
                                                                                             op=operator))
                    else:
                        if 5 <= randint(1, 10):
                            piece_strings.append('')
                        else:
                            pass
                else:
                    piece_strings.append("{jobid},{pieceid},{time},{result},{op}".format(jobid=job_string,
                                                                                         pieceid=str(i).zfill(6),
                                                                                         time=self.curr_time,
                                                                                         result=choice(['1', '2']),
                                                                                         op=operator))
                if i % self.speed == 0:
                    self.curr_time = self.add_seconds(self.curr_time, 1)
            else:
                piece_strings.append("{jobid},{pieceid},{time},{result},{op}".format(jobid=job_string,
                                                                                     pieceid=str(i).zfill(6),
                                                                                     time=self.curr_time,
                                                                                     result='0',
                                                                                     op=operator))
                if i % self.speed == 0:
                    self.curr_time = self.add_seconds(self.curr_time, 1)

        filename = path.join(out_path, "piece_" + job_string + ".txt")
        logger.debug('Writing Piece File.')
        with open(filename, 'w') as fp:
            fp.write(out_str.join(piece_strings) + '\n')
        fp.close()
        self.curr_time = None
        return damage_list

    def gen_reprints(self, damage_list):
        out_str = "\n"
        out_path = folder_construct()
        reprint_strings = []
        if self.multi_step == 1 or self.target == 'td':
            self.curr_time = datetime.datetime.now()
        else:
            self.curr_time = self.creation[1] + datetime.timedelta(hours=2)
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        operator = None
        ostrings = []

        if find_shift() == 1:
            for k in self.reprinters.keys():
                if self.reprinters[k]['shift1']:
                    for t in self.reprinters[k]['shift1'].split(','):
                        ostrings.append(t)
            operator = choice(ostrings)
        if find_shift() == 2:
            for k in self.reprinters.keys():
                if self.reprinters[k]['shift2']:
                    for t in self.reprinters[k]['shift1'].split(','):
                        ostrings.append(t)
            operator = choice(ostrings)
        if find_shift() == 3:
            for k in self.reprinters.keys():
                if self.reprinters[k]['shift3']:
                    for t in self.reprinters[k]['shift1'].split(','):
                        ostrings.append(t)
            operator = choice(ostrings)

        unique_damages = [i for i in set(damage_list)]

        for i in unique_damages:
            reprint_strings.append("{jobid},{pieceid},{time},{result},{op}".format(jobid=job_string,
                                                                                   pieceid=str(i).zfill(6),
                                                                                   time=self.curr_time,
                                                                                   result='0',
                                                                                   op=operator))
            if i % self.r_speed == 0:
                self.curr_time = self.add_seconds(self.curr_time, 1)

        filename = path.join(out_path, "reprint_" + job_string + ".txt")
        logger.debug('Writing Reprint File.')
        with open(filename, 'w') as fp:
            fp.write(out_str.join(reprint_strings) + '\n')
        fp.close()
        self.curr_time = None
