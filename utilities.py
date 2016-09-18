import config
import os
import json
import psutil
import datetime
import time
from logging_setup import init_logging

logger = init_logging()


def clean_reprints(control):
    count = 0
    path_to_reprints = control.democonf[1]['APTDirs']['REPRINT']
    reprints = [i for i in os.listdir(control.democonf[1]['APTDirs']['REPRINT'])]
    for file in reprints:
        os.remove(os.path.join(path_to_reprints, file))
        count += 1
    return count


def clean_td(control):
    count = 0
    path_to_td = control.democonf[0]['td']['path']
    td_files = [i for i in os.listdir(control.democonf[0]['td']['path'])]
    for file in td_files:
        os.remove(os.path.join(path_to_td, file))
        count += 1
    return count


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


def sysTimeStamp(timeval):
    """
    Formats a raw time value into a formatted string in a standard format.
    :param timeval:
    :return:
    """
    return datetime.datetime.fromtimestamp(timeval).strftime("%Y-%m-%d %H:%M:%S")


class ResourceSnapshot:
    """
    Creates a snapshot of system information as an object.
    """
    def __init__(self):
        sysmem = psutil.virtual_memory()
        proc = psutil.Process()
        proc_io = proc.io_counters()
        proc_mem = proc.memory_info()
        self._time = time.time()
        self._boot_time = psutil.boot_time()
        self._sysmem_available = sysmem.available
        self._sysmem_total = sysmem.total
        self._sysmem_percent = sysmem.percent
        self._proc_create_time = proc.create_time()
        self._proc_rss = proc_mem.rss
        self._proc_io_read = proc_io.read_count
        self._proc_io_write = proc_io.write_count

    def system_boot_time(self, raw: bool=False):
        """
        Returns the host machine's boot time.
        If raw is True, it returns the raw time value, otherwise
        it formats it using to sysTimeStamp().
        :param raw:
        :return:
        """
        if raw:
            return self._boot_time
        else:
            return sysTimeStamp(self._boot_time)

    def system_memory_available(self, raw: bool=False):
        """
        Returns the current amount of system RAM available.
        If raw is True, the number is in bytes, otherwise
        it is in megabytes.
        :param raw:
        :return:
        """
        if raw:
            return self._sysmem_available
        else:
            return self._sysmem_available // (1024 * 1024)

    def system_memory_total(self, raw: bool=False):
        """
        Returns the total amount of RAM in the system.
        If raw is True, the number is in bytes, otherwise
        it is in megabytes.
        :param raw:
        :return:
        """
        if raw:
            return self._sysmem_total
        else:
            return self._sysmem_total // (1024 * 1024)

    def system_memory_percent_used(self):
        """
        Returns the percentage of system memory in use.
        :return:
        """
        return self._sysmem_percent

    def process_start_time(self, raw: bool=False):
        """
        Returns the time this process started running.
        If raw is True, it returns the raw time value, otherwise
        it formats it using to sysTimeStamp().
        :param raw:
        :return:
        """
        if raw:
            return self._proc_create_time
        else:
            return sysTimeStamp(self._proc_create_time)

    def current_time(self, raw: bool=False):
        """
        Returns the time the snapshot was taken.
        If raw is True, it returns the raw time value, otherwise
        it formats it using to sysTimeStamp().
        :param raw:
        :return:
        """
        if raw:
            return self._time
        else:
            return sysTimeStamp(self._time)

    def process_memory(self, raw: bool=False):
        """
        Returns the RSS size of the process.
        If raw is True, the number is in bytes, otherwise
        it is in megabytes.
        :param raw:
        :return:
        """
        if raw:
            return self._proc_rss
        else:
            return self._proc_rss // (1024 * 1024)

    def process_io(self, write: bool=False):
        """
        Returns the number of I/O operations the process has performed.
        If write is True, it returns the number of output operations,
        otherwise it returns the number of input operations.
        :param write:
        :return:
        """
        if write:
            return self._proc_io_write
        else:
            return self._proc_io_read

    def log_data(self):
        """
        Returns a string that has been formatted for output through
        the logging system, as we've defined it in all our code.
        If you change the output formatting of the logs, you should
        also change this code to match.
        :return:
        """
        results = (
            'Snapshot time: %s' % (self.current_time()),
            'System booted at: %s' % (self.system_boot_time()),
            'System has %dM of %dM available (%.3f%% used)' % (self.system_memory_available(),
                                                               self.system_memory_total(),
                                                               self.system_memory_percent_used()),
            'Driver started at: %s' % (self.process_start_time()),
            'Driver is currently using %dM of RAM' % (self.process_memory()),
            'Driver has performed %d read and %d write I/O operations.' % (self.process_io(),
                                                                           self.process_io(True)),
        )
        spaces = '\n' + ' ' * 51
        output = spaces.join(results)
        return output
