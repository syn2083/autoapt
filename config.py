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

DEF_DEMO_CONF = [{'icd_1': {'path': 'C:/APTApplication/ICD/icd_1', 'sph': 60000, 'piece_sheet': 'sheet',
                            'multi_step': 1},
                  'icd_2': {'path': 'C:/APTApplication/ICD/icd_2', 'sph': 12000, 'piece_sheet': 'piece',
                            'multi_step': 0},
                  'icd_3': {'path': 'C:/APTApplication/ICD/icd_3', 'sph': 20000, 'piece_sheet': 'piece',
                            'multi_step': 0},
                  'icd_4': {'path': 'C:/APTApplication/ICD/icd_4', 'sph': 6000, 'piece_sheet': 'piece',
                            'multi_step': 0},
                  'td': {'path': 'C:/APTApplication/ICD/tdinput', 'sph': 12000, 'piece_sheet': 'piece',
                         'multi_step': 0}},
                 {'APTDirs': {'JDF': 'C:/APTApplication/Server/Inputs/JDFInput',
                              'JIFACK': 'C:/APTApplication/Server/Inputs/JIFAcks',
                              'PROC': 'C:/APTApplication/Server/Outputs/WIP',
                              'REPRINT': 'C:/APTApplication/Server/Outputs/ReprintFiles'},
                  'DemoDirs': {'exit_data': EXIT_DATA, 'jif_data': JIF_DATA}}]

DEF_JIF_CONF = [{'JIF': {'temp_name': 'APTDemo', 'jtype': 'Checks, Statements, New Member', 'jnum': '0001, 9000',
                         'jclass': 'XG1, DP99, A1, C3', 'jname': '0X-', 'jpref': 'A',
                         'actid': 'National Bank, Insurance Unlimited, MA Tech, Ironsides', 'prodname': 'C33, BQ1, XD3',
                         'prodloc': 'Westford', 'envid': '10, 6x9, 9x12', 'stockid': 'A3, GL5, BB4',
                         'stocktype': 'Matte, Gloss', 'ui1': '', 'ui2': '', 'ui3': '', 'ui4': '', 'ui5': '',
                         'cemail': 'support@ironsidestech.com'},
                 'OPTS': {'prange': '500, 1000', 'srange': '1, 8', 'num_jifs': 1,
                          'shift1': 'Jim, John, Amy, Ashley, Alec, Paul, Zach, Ted, Sharon',
                          'shift2': 'Kent, Laura, Chris, Erin, Susan, Pete, Wendy, Sara, Ken',
                          'shift3': 'Jason, Ray, Sean, Bill, Tom, Roman, Dennis, Henry, Heather'}}]

