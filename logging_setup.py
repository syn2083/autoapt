import logging
import os
import config

master_logger = None

print(config.BASE_DIR)

def init_logging():
    global master_logger
    if master_logger is None:
        print(config.log_dir)
        if not os.path.exists(config.log_dir):
            print('no dir found..')
            os.makedirs(config.log_dir)
            with open(config.log_file, 'w') as fp:
                fp.write('---Logging Init---')

        logging.basicConfig(filename='{}'.format(config.log_file),
                            level=logging.DEBUG,
                            format='[%(levelname)s] %(module)s-%(asctime)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        master_logger = logging.getLogger()
    return master_logger
