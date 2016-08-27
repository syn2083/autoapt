import datetime
import os
import shutil
from random import choice, randint, sample
from os import path
from .jif_templater import Template
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


class JIFBuilder(Template):
    def __init__(self, icd_target, jdf_folder, multi_step, dconf, jconf):
        super().__init__()
        for k in jconf.keys():
            setattr(self, k, jconf[k])
        self.out = jdf_folder
        self.target = icd_target
        self.multi_step = multi_step
        if icd_target == 'icd_1':
            self.site_prefix = 'A10'
            self.proc_phase = '10, 30'
            self.end_phase = '30'
            self.piece_or_sheet = dconf[0]['icd_1']['piece_sheet']
            self.speed = ((dconf[0]['icd_1']['sph'] // 60) // 60)
        if icd_target == 'icd_2':
            self.site_prefix = 'A20'
            self.proc_phase = '20'
            self.end_phase = '20'
            self.piece_or_sheet = dconf[0]['icd_2']['piece_sheet']
            self.speed = ((dconf[0]['icd_2']['sph'] // 60) // 60)
        if icd_target == 'icd_3':
            self.site_prefix = 'A30'
            self.proc_phase = '30'
            self.end_phase = '30'
            self.piece_or_sheet = dconf[0]['icd_3']['piece_sheet']
            self.speed = ((dconf[0]['icd_3']['sph'] // 60) // 60)
        if icd_target == 'td':
            self.site_prefix = 'A40'
            self.proc_phase = '30'
            self.end_phase = '30'
            self.piece_or_sheet = 'piece'
            self.speed = 1
        self.r_speed = 2

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

        self.jobid_loader()
        logger.debug('Starting to build JIF {}{}.'.format(self.site_prefix, self.id_to_str(self.current_jobid)))
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

        for k,v in conv_dict.items():
            v[1] = str_to_list(v[0])

        if 4 <= randint(1, 10):
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
            jif_strings.append(" <JobNumber>{}</JobNumber>".format(choice(conv_dict['jnum'][1])))
            jif_strings.append(" <ProductName>{}</ProductName>".format(choice(conv_dict['prodname'][1])))
            jif_strings.append(" <AccountID>{}</AccountID>".format(choice(conv_dict['actid'][1])))
            jif_strings.append(" <StartSequence>000001</StartSequence>")
            count = [i.strip() for i in self.prange.split(',')]
            self.current_piececount = randint(int(count[0]), int(count[1]))
            jif_strings.append(" <EndSequence>{}</EndSequence>".format(str(self.current_piececount).zfill(6)))
            jif_strings.append(" <PieceCount>{}</PieceCount>".format(str(self.current_piececount)))
            jif_strings.append(" <CreationDate>{}</CreationDate>".format(self.creation[0]))
            jif_strings.append(" <JobDeadLine/>")
            jif_strings.append(" <PrintMode>1</PrintMode>\n <PageComposition>2</PageComposition>")
            jif_strings.append(" <ProcessingPhases>{}</ProcessingPhases>".format(self.proc_phase))
            jif_strings.append(" <EndProcess>{}</EndProcess>".format(self.end_phase))
            jif_strings.append(" <ProductionLocation>{}</ProductionLocation>".format(choice(conv_dict['prodloc'][1])))
            jif_strings.append(" <Class>{}</Class>".format(choice(conv_dict['jclass'][1])))
            jif_strings.append(" <EnvelopeID>{}</EnvelopeID>".format(choice(conv_dict['envid'][1])))
            jif_strings.append(" <StockID>{}</StockID>".format(choice(conv_dict['stockid'][1])))
            jif_strings.append(" <StockType>{}</StockType>".format(choice(conv_dict['stocktype'][1])))
            jif_strings.append(" <UserInfo1>{}</UserInfo1>".format(choice(conv_dict['ui1'][1])))
            jif_strings.append(" <UserInfo2>{}</UserInfo2>".format(choice(conv_dict['ui2'][1])))
            jif_strings.append(" <UserInfo3>{}</UserInfo3>".format(choice(conv_dict['ui3'][1])))
            jif_strings.append(" <UserInfo4>{}</UserInfo4>".format(choice(conv_dict['ui4'][1])))
            jif_strings.append(" <UserInfo5>{}</UserInfo5>".format(choice(conv_dict['ui5'][1])))
            # jif_strings.append("  <JobManifest>")
            logger.debug('Building Sheets.')
            for t in range(1, self.current_piececount + 1):
                result = self.piece_builder(t)
                # jif_strings.append(result[0])
                sheet_list.append(result[1])
            # jif_strings.append("  </JobManifest>")
            multi = int(choice(conv_dict['imp_mult'][1]))
            sheets = 0
            for x in sheet_list:
                sheets += x
            scount = sheets
            jif_strings.append(" <SheetCount>{sheet_count}</SheetCount>".format(sheet_count=scount))
            jif_strings.append(" <PageCount>{page_count}</PageCount>".format(page_count=(multi * scount)))
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
                        self.gen_reprints(reprint_set, conv_dict)
                    else:
                        self.gen_sheet_data(create_damages=0, num_sheets=sheet_list, ops=conv_dict)
                        self.gen_piece_data(create_damages=0, ops=conv_dict)
                if make_damages:
                    self.gen_sheet_data(create_damages=1, num_sheets=sheet_list, ops=conv_dict)
            if self.piece_or_sheet.lower() == 'piece':
                if make_damages:
                    piece_reprints = self.gen_piece_data(create_damages=1, ops=conv_dict)
                    self.gen_reprints(piece_reprints, conv_dict)
                else:
                    self.gen_piece_data(ops=conv_dict)

            present_jobid = '{}{}'.format(self.site_prefix, str(self.current_jobid).zfill(7))
            self.current_jobid += 1
            self.generated_jobs += 1
            logger.debug('Saving Job Seed')
            self.jobid_saver()
            temp_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output\\aptdemo\\jif_output')
            filename = path.join(temp_folder, present_jobid + ".jif")
            with open(filename, 'w') as fp:
                fp.write(jstr)
            fp.close()
            logger.debug('Copying JIF to JDF folder.')
            shutil.copyfile(filename, os.path.join(self.out, present_jobid + '.jif'))
            logger.debug('Cleaning temp JIF')
            os.remove(filename)
            logger.debug('JIF creation completed. {} has been sent to APT.'.format(present_jobid))
            return present_jobid

    def gen_sheet_data(self, create_damages=None, num_sheets=None, ops=None):
        out_str = "\n"
        out_path = folder_construct()[2]
        sheet_strings = []
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        self.curr_time = self.creation[1]
        sheet_count = 0
        damage_list = []
        operator = None

        if find_shift() == 1:
            operator = choice(ops['shift_1_ops'][1])
        if find_shift() == 2:
            operator = choice(ops['shift_2_ops'][1])
        if find_shift() == 3:
            operator = choice(ops['shift_3_ops'][1])

        if create_damages:
            damage_list = sample(range(1, self.current_piececount), choice([1, 5, 10, 15, 20, 25]))

        for n, i in enumerate(range(1, self.current_piececount + 1)):
            if 'piece' in self.piece_or_sheet.lower():
                if n % self.speed == 0:
                    self.curr_time = self.add_seconds(self.curr_time, 1)
            for t in range(1, num_sheets[i - 1] + 1):
                if i in damage_list:
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
        return damage_list

    def gen_piece_data(self, create_damages=0, ops=None):
        out_str = "\n"
        out_path = folder_construct()[2]
        piece_strings = []
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        damage_list = []
        operator = None

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
                damage_list = sample(range(1, self.current_piececount), choice([1, 5, 10, 15, 20, 25]))

        for i in range(1, self.current_piececount + 1):
            if i in damage_list:
                if self.multi_step or self.target.lower() == 'td':
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

    def gen_reprints(self, damage_list, ops):
        out_str = "\n"
        out_path = folder_construct()[2]
        reprint_strings = []
        self.curr_time = self.creation[1] + datetime.timedelta(hours=2)
        job_string = self.site_prefix + str(self.current_jobid).zfill(7)
        operator = None

        if find_shift() == 1:
            operator = choice(ops['shift_1_ops'][1])
        if find_shift() == 2:
            operator = choice(ops['shift_2_ops'][1])
        if find_shift() == 3:
            operator = choice(ops['shift_3_ops'][1])

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
