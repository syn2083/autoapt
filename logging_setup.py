import logging
import os
import config
import shutil
import datetime

master_logger = None


def init_logging():
    global master_logger
    if master_logger is None:
        if not os.path.exists(config.log_dir):
            os.makedirs(config.log_dir)
            with open(config.log_file, 'w') as fp:
                fp.write('---Logging Init---')

        logging.basicConfig(filename='{}'.format(config.log_file),
                            level=logging.DEBUG,
                            format='[%(levelname)-7s] %(asctime)s %(module)15s| %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        master_logger = logging.getLogger()
    return master_logger


def check_log():
    file_size = os.path.getsize(config.log_file)
    dated_files = [(os.path.getmtime(os.path.join(config.log_dir, fn)), os.path.basename(fn))
                   for fn in os.listdir(config.log_dir)]
    dated_files.sort()

    # Only keep about 5 log files at once
    if 5 > len(dated_files):
        for i in range(0, len(dated_files) - 5):
            os.remove(os.path.join(config.log_dir, dated_files[0][i]))

    # Rotate log if it is over 1MB in size
    if file_size >= 8388608:
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        old_log = os.path.join(config.log_dir, )
        shutil.copy(config.log_file, '{}.log'.format(now))
        with open(config.log_file, 'w') as fp:
            fp.write('---Logging Init---')



