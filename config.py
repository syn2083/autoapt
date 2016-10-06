__author__ = 'Syn'
import os
import configparser

# Logger Configs
scriptdir, script = os.path.split(__file__)
BASE_DIR = scriptdir
# For packaged
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
DEMO_CONF_DIR = os.path.join(BASE_DIR, 'config_files')
DEMO_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'demo.config')
JIF_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'jif.config')

"""Learned about configparser after doing all this.. refactor in the future."""
# TODO utilize config-parser instead of this
DEF_DEMO_CONF = [{'icd_1': {'origin': 'icd_1', 'path': 'C:/APTApplication/ICD/icd_1', 'speed': 60000,
                            'piece_or_sheet': 'sheet', 'multi_step': 1, 'site_prefix': 'A10', 'shift1': 'Jim, John, Amy',
                            'shift2': 'Kent, Laura, Chris', 'shift3': 'Jason, Ray, Sean', 'proc_phase': '10, 30',
                            'end_phase': '30', 'jobid': []},
                  'icd_2': {'origin': 'icd_2', 'path': 'C:/APTApplication/ICD/icd_2', 'speed': 12500,
                            'piece_or_sheet': 'piece', 'multi_step': 0, 'site_prefix': 'A20',
                            'shift1': 'Ashley, Alec, Paul', 'shift2': 'Erin, Susan, Pete',
                            'shift3': 'Bill, Tom, Roman', 'proc_phase': '20', 'end_phase': '20', 'jobid': []},
                  'icd_3': {'origin': 'icd_3', 'path': 'C:/APTApplication/ICD/icd_3', 'speed': 22000,
                            'piece_or_sheet': 'piece', 'multi_step': 0, 'site_prefix': 'A30',
                            'shift1': 'Zach, Ted, Sharon', 'shift2': 'Wendy, Sara, Ken',
                            'shift3': 'Dennis, Henry, Heather', 'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'icd_4': {'origin': 'icd_4', 'path': 'C:/APTApplication/ICD/icd_4', 'speed': 6000,
                            'piece_or_sheet': 'reprint', 'multi_step': 0, 'site_prefix': 'A00',
                            'shift1': 'Todd, Jeff, Lisa', 'shift2': 'Diane, Greg, James',
                            'shift3': 'Harrold, Doug, Joseph', 'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'icd_5': {'origin': 'icd_5', 'path': 'C:/APTApplication/ICD/icd_5', 'speed': 6000,
                            'piece_or_sheet': 'reprint', 'multi_step': 0, 'site_prefix': 'A00', 'shift1': '',
                            'shift2': '', 'shift3': '', 'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'icd_6': {'origin': 'icd_6', 'path': 'C:/APTApplication/ICD/icd_6', 'speed': 6000,
                            'piece_or_sheet': 'reprint', 'multi_step': 0, 'site_prefix': 'A00', 'shift1': '',
                            'shift2': '', 'shift3': '', 'proc_phase': '30', 'end_phase': '30', 'jobid': []},
                  'td': {'origin': 'td', 'path': 'C:/APTApplication/ICD/tdinput', 'speed': 17500,
                         'piece_or_sheet': 'piece', 'multi_step': 0, 'site_prefix': 'A40', 'shift1': '',
                         'shift2': '', 'shift3': '', 'proc_phase': '30', 'end_phase': '30', 'jobid': []}},
                 {'APTDirs': {'JDF': 'C:/APTApplication/Server/Inputs/JDFInput',
                              'JIFACK': 'C:/APTApplication/Server/Inputs/JIFAcks',
                              'PROC': 'C:/APTApplication/Server/Outputs/WIP',
                              'REPRINT': 'C:/APTApplication/Server/Outputs/ReprintFiles'},
                  'DemoDirs': {'exit_data': EXIT_DATA, 'jif_data': JIF_DATA}},
                 {'active_targets': ['icd_1', 'icd_2', 'icd_3', 'td'],
                  'reprint_pool': ['icd_4', 'icd_5', 'icd_6'],
                  'all_targets': ['icd_1', 'icd_2', 'icd_3', 'icd_4', 'icd_5', 'icd_6', 'td']}]

DEF_JIF_CONF = [{'JIF': {'temp_name': 'APTDemo', 'jtype': 'Checks, Statements, New Member', 'jnum': '0001, 9000',
                         'jclass': '8.5x11, 9x12, 11x17', 'jname': 'Color, B+W', 'jpref': 'A',
                         'actid': 'National Bank, Insurance Unlimited, MA Tech, Ironsides', 'prodname': 'C33, BQ1, XD3',
                         'prodloc': 'Westford', 'envid': '10, 6x9, 9x12', 'stockid': 'A3, GL5, BB4',
                         'stocktype': 'Matte, Gloss', 'ui1': 'Saddle Stitch, Perfect Bind',
                         'ui2': '10, 6x9, 9x12', 'ui3': '0X-, 1D-, AQ-', 'ui4': '', 'ui5': '',
                         'cemail': 'support@ironsidestech.com'},
                'OPTS': {'prange': '1000, 1600', 'srange': '1, 4', 'num_jifs': 1}}]


def save_default_sys():
    if not os.path.isfile(os.path.join(DEMO_CONF_DIR, 'sys.ini')):
        with open(os.path.join(DEMO_CONF_DIR, 'sys.ini'), 'w') as syscfg:
            config = configparser.ConfigParser()
            http = 'HTTPServer'
            sock = 'SocketServer'
            db = 'DB'
            mode = 'Mode'
            config.add_section(http)
            config.set(http, 'host', '0.0.0.0')
            config.set(http, 'port', '8888')
            config.add_section(sock)
            config.set(sock, 'host', '0.0.0.0')
            config.set(sock, 'port', '8091')
            config.add_section(db)
            config.set(db, 'dbname', 'aptdemo.db')
            config.add_section(mode)
            config.set(mode, 'connection_type', 'file')
            config.write(syscfg)


def save_default_demo():
    if not os.path.isfile(os.path.join(DEMO_CONF_DIR, 'demo.ini')):
        with open(os.path.join(DEMO_CONF_DIR, 'demo.ini'),  'w') as democfg:
            config = configparser.ConfigParser()
            for i in DEF_DEMO_CONF:
                for k, v in i.items():
                    config.add_section(k)
                    if isinstance(v, list):
                        config.set(k, k, ', '.join(v))
                    else:
                        for nk, nv in v.items():
                            config.set(k, nk, str(nv))
            config.write(democfg)


def save_default_jif():
    if not os.path.isfile(os.path.join(DEMO_CONF_DIR, 'jif.ini')):
        with open(os.path.join(DEMO_CONF_DIR, 'jif.ini'), 'w') as jifcfg:
            config = configparser.ConfigParser()
            for i in DEF_JIF_CONF:
                for k, v in i.items():
                    config.add_section(k)
                    if isinstance(v, list):
                        config.set(k, k, ', '.join(v))
                    else:
                        for nk, nv in v.items():
                            config.set(k, nk, str(nv))
            config.write(jifcfg)


def parse_demo_config(config):
    """
    Takes the demo ini file, parses out the values as I need them, and passes back a list of the 3 archetypes used for
    the system
    :param config:
    :type config: configparser object
    :return: list[dict, dict, dict]
    :rtype: list
    """
    out = []
    icd_dict = {}
    targets = {}
    dirs = {}

    for k in config.keys():
        # Pull out the icd/td sections, and re-construct the dicts
        if k[:2] in ('ic', 'td'):
            x = {}
            for subk, subv in config[k].items():
                # Rebuild the jobid list section
                if '[]' in subv:
                    x[subk] = []
                else:
                    try:
                        # Reconstitute ints
                        x[subk] = int(subv)
                    except ValueError:
                        # Leave strings/string lists alone
                        x[subk] = subv
            icd_dict[k] = x

        # Pull out the target sections and re-construct the dicts
        if k[:3] in ('act', 'rep', 'all'):
            targets[k] = [i.strip() for z in config[k].values() for i in z.split(',')]

        # Pull out the dirs sections and re-construct the dicts
        if 'Dirs' in k:
            y = {}
            for subk, subv in config[k].items():
                y[subk] = subv
            dirs[k] = y

    out.append(icd_dict)
    out.append(dirs)
    out.append(targets)

    return out


def parse_sys_config(config):
    out = {}
    for k in config.keys():
        if 'HTTP' in k:
            x = {}
            for subk, subv in config[k].items():
                try:
                    x[subk] = int(subv)
                except ValueError:
                    x[subk] = subv
            out[k] = x
        if 'Socket' in k:
            y = {}
            for subk, subv in config[k].items():
                try:
                    y[subk] = int(subv)
                except ValueError:
                    y[subk] = subv
            out[k] = y
        if 'DB' in k:
            z = {}
            for subk, subv in config[k].items():
                z[subk] = subv
            out[k] = z
        if 'Mode' in k:
            z = {}
            for subk, subv in config[k].items():
                z[subk] = subv
            out[k] = z

    return out


def parse_jif_config(config):
    jif = {}
    out = []

    for k in config.keys():
        if 'JIF' in k:
            x = {}
            for subk, subv in config[k].items():
                x[subk] = subv
            jif[k] = x

        if 'OPTS' in k:
            y = {}
            for subk, subv in config[k].items():
                try:
                    y[subk] = int(subv)
                except ValueError:
                    y[subk] = subv
            jif[k] = y

    out.append(jif)

    return out


def load_config(target):
    out = {}
    config = configparser.ConfigParser()
    for starget in target.split(','):
        config.read(os.path.join(DEMO_CONF_DIR, '{}.ini'.format(starget.strip())))
    if 'demo' in target:
        out['dconf'] = parse_demo_config(config)

    if 'sys' in target:
        out['sysconf'] = parse_sys_config(config)

    if 'jif' in target:
        out['jconf'] = parse_jif_config(config)

    return out
