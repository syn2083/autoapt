__author__ = 'Syn'
import os


BASE_DIR = os.getcwd()

# Logger Configs
log_dir = os.path.join(BASE_DIR, 'logs')
log_file = os.path.join(log_dir, 'aptdemo.log')

# JIF Generator Dir
JIFGEN = os.path.join(BASE_DIR, 'jifgenerator')
EXIT_DATA = os.path.join(JIFGEN, 'output/APTDemo/exit_data')
JIF_DATA = os.path.join(JIFGEN, 'output/APTDemo/jif_data')

# Socket Server Configs
SERV_ADDR = '127.0.0.1'
SOCK_PORT = 8091
CHUNK_SIZE = 4096

# System Configs
DEMO_CONF_DIR = os.path.join(os.getcwd(), 'config_files')
DEMO_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'demo.config')
JIF_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'jif.config')

DEF_DEMO_CONF = [{'icd_1': {'path': 'C:/APTApplication/ICD/icd_1', 'speed': 60000, 'piece_or_sheet': 'sheet',
                            'multi_step': 1, 'site_prefix': 'A10', 'shift1': 'Jim, John, Amy', 'shift2': 'Kent, Laura, Chris',
                            'shift3': 'Jason, Ray, Sean', 'proc_phase': '10, 30', 'end_phase': '30', 'jobid': []},
                  'icd_2': {'path': 'C:/APTApplication/ICD/icd_2', 'speed': 12000, 'piece_or_sheet': 'piece',
                            'multi_step': 0, 'site_prefix': 'A20', 'shift1': 'Ashley, Alec, Paul',
                            'shift2': 'Erin, Susan, Pete', 'shift3': 'Bill, Tom, Roman', 'proc_phase': '20',
                            'end_phase': '20', 'jobid': []},
                  'icd_3': {'path': 'C:/APTApplication/ICD/icd_3', 'speed': 20000, 'piece_or_sheet': 'piece',
                            'multi_step': 0, 'site_prefix': 'A30', 'shift1': 'Zach, Ted, Sharon',
                            'shift2': 'Wendy, Sara, Ken', 'shift3': 'Dennis, Henry, Heather', 'proc_phase': '30',
                            'end_phase': '30', 'jobid': []},
                  'icd_4': {'path': 'C:/APTApplication/ICD/icd_4', 'speed': 6000, 'piece_or_sheet': 'piece',
                            'multi_step': 0, 'site_prefix': 'A00', 'shift1': 'Todd, Jeff, Lisa',
                            'shift2': 'Diane, Greg, James', 'shift3': 'Harrold, Doug, Joseph', 'proc_phase': '30',
                            'end_phase': '30', 'jobid': []},
                  'icd_5': {'path': 'C:/APTApplication/ICD/icd_5', 'speed': 6000, 'piece_or_sheet': 'piece',
                            'multi_step': 0, 'site_prefix': 'A00', 'shift1': '', 'shift2': '', 'shift3': '',
                            'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'icd_6': {'path': 'C:/APTApplication/ICD/icd_6', 'speed': 6000, 'piece_or_sheet': 'piece',
                            'multi_step': 0, 'site_prefix': 'A00', 'shift1': '', 'shift2': '', 'shift3': '',
                            'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'td': {'path': 'C:/APTApplication/ICD/tdinput', 'speed': 12000, 'piece_or_sheet': 'piece',
                         'multi_step': 0, 'site_prefix': 'A40', 'shift1': '', 'shift2': '', 'shift3': '',
                         'proc_phase': '30', 'end_phase': '30', 'jobid': []}},
                 {'APTDirs': {'JDF': 'C:/APTApplication/Server/Inputs/JDFInput',
                              'JIFACK': 'C:/APTApplication/Server/Inputs/JIFAcks',
                              'PROC': 'C:/APTApplication/Server/Outputs/WIP',
                              'REPRINT': 'C:/APTApplication/Server/Outputs/ReprintFiles'},
                  'DemoDirs': {'exit_data': EXIT_DATA, 'jif_data': JIF_DATA}},
                 {'active_targets': ['icd_1', 'icd_2', 'icd_3', 'td'],
                  'reprint_pool': ['icd_4', 'icd_5', 'icd_6'],
                  'all_targets': ['icd_1', 'icd_2', 'icd_3', 'icd_4', 'icd_5', 'icd_6', 'td']}]

DEF_JIF_CONF = [{'JIF': {'temp_name': 'APTDemo', 'jtype': 'Checks, Statements, New Member', 'jnum': '0001, 9000',
                         'jclass': 'XG1, DP99, A1, C3', 'jname': '0X-', 'jpref': 'A',
                         'actid': 'National Bank, Insurance Unlimited, MA Tech, Ironsides', 'prodname': 'C33, BQ1, XD3',
                         'prodloc': 'Westford', 'envid': '10, 6x9, 9x12', 'stockid': 'A3, GL5, BB4',
                         'stocktype': 'Matte, Gloss', 'ui1': '', 'ui2': '', 'ui3': '', 'ui4': '', 'ui5': '',
                         'cemail': 'support@ironsidestech.com'},
                'OPTS': {'prange': '500, 1000', 'srange': '1, 8', 'num_jifs': 1}}]

