import sys
import config
import os
import json
import psutil
import pprint
from logging_setup import init_logging

logger = init_logging()


def init_configs():
    demo_file = None
    jif_file = None

    logger.info('--Config Initialization--')
    if not os.path.exists(config.DEMO_CONF_DIR):
        logger.info('--Creating Config Directory--')
        os.makedirs(config.DEMO_CONF_DIR)

    try:
        logger.info('Loading Demo Config')
        with open(config.DEMO_CONF_FILE, 'r') as fp:
            demo_file = json.loads(fp.read())
    except FileNotFoundError:
        logger.error('--Demo Config not found, Loading Default--')
        demo_file = config.DEF_DEMO_CONF
        dconfig = json.dumps(config.DEF_DEMO_CONF)
        with open(config.DEMO_CONF_FILE, 'w') as fp:
            fp.write(dconfig)

    try:
        logger.info('Loading JIF Config')
        with open(config.JIF_CONF_FILE, 'r') as fp:
            jif_file = json.loads(fp.read())
    except FileNotFoundError:
        logger.error('--JIF Config not found, Loading Default--')
        jif_file = config.DEF_JIF_CONF
        jconfig = json.dumps(config.DEF_JIF_CONF)
        with open(config.JIF_CONF_FILE, 'w') as fp:
            fp.write(jconfig)

    return demo_file, jif_file


def sys_snapshot():
    proc = psutil.Process()
    pp = pprint.PrettyPrinter(indent=4)
    snappy = {'Sys Info': {'Boot Time': proc.create_time(), 'Process Name': proc.name(), 'Status': proc.status()},
              'Hardware': {'CPU': {'Cores': psutil.cpu_count(), 'Current Utilization': proc.cpu_percent(),
                                   'Threads': proc.num_threads()},
                           'RAM': {'Stats': proc.memory_info(), '% of Memory': proc.memory_percent()},
                           'HDD': {'Disk Usage': psutil.disk_usage('/'), 'I/O': psutil.disk_io_counters()},
                           'NIC': {'I/O': psutil.net_io_counters()}}}
    snap_string = pp.pformat(snappy)
    return snappy, snap_string
