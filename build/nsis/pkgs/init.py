__author__ = 'Syn'
import threading
import os
import config
import json
from controller import DemoController
from logging_setup import init_logging
from dispatcher import Dispatcher

logger = init_logging()


def init_controller():
    dconf = None
    jconf = None
    if not os.path.exists(config.DEMO_CONF_DIR):
        os.makedirs(config.DEMO_CONF_DIR)
    try:
        with open(config.DEMO_CONF_FILE, 'r') as fp:
            output = fp.read()
            dconf = json.loads(output)
    except FileNotFoundError:
        logger.boot('Demo config file not found, creating from template..')
        with open(config.DEMO_CONF_FILE, 'w') as fp:
            output = json.dumps(config.DEF_DEMO_CONF)
            fp.write(output)
            dconf = config.DEF_DEMO_CONF
    try:
        with open(config.JIF_CONF_FILE, 'r') as fp:
            output = fp.read()
            jconf = json.loads(output)
    except FileNotFoundError:
        logger.boot('JIF config file not found, creating from template..')
        with open(config.JIF_CONF_FILE, 'w') as fp:
            output = json.dumps(config.DEF_JIF_CONF)
            fp.write(output)
            jconf = config.DEF_JIF_CONF

    control = DemoController(dconf, jconf)
    control.lock = threading.Lock()
    control.dispatcher = Dispatcher(control)
    control.dispatcher.start()

    return control

