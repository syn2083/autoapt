__author__ = 'Syn'
import os
import config
import threading
from file_mon import file_handler
from controller import DemoController, DataController
from logging_setup import init_logging
from dispatcher import Dispatcher
from webinterface import aptinterface
from tornado import ioloop
from watchdog.observers import Observer

logger = init_logging()


def init_web_server(host, port):
    web_server = aptinterface.server
    web_server.listen(port, address=host)
    ioloop.IOLoop.instance().start()


def init_controller():
    if not os.path.exists(config.DEMO_CONF_DIR):
        os.makedirs(config.DEMO_CONF_DIR)
    ini_files = ['sys.ini', 'demo.ini', 'jif.ini']

    for file in ini_files:
        if not os.path.isfile(os.path.join(config.DEMO_CONF_DIR, file)):
            if 'sys' in file:
                logger.boot('System ini not found, saving default')
                config.save_default_sys()
            elif 'demo' in file:
                logger.boot('Demo ini not found, saving default')
                config.save_default_demo()
            elif 'jif' in file:
                logger.boot('JIF ini not found, saving default')
                config.save_default_jif()

    configs = config.load_config('sys, demo, jif')

    control = DemoController(configs['dconf'], configs['jconf'], configs['sysconf'])
    control.lock = threading.Lock()

    # Dispatcher setup
    control.dispatcher = Dispatcher(control)
    control.dispatcher.start()

    # Data controller
    control.data_controller = DataController(control.all_targets, control.reprint_pool,
                                             configs['dconf'][0], control.exit_dir)
    control.data_controller.setup_workers()

    # File observer setups
    proc_observer = Observer()
    proc_observer.schedule(file_handler.StatusChange(control.proc_queue), control.proc_dir)
    control.observers.append(proc_observer)
    proc_observer.start()
    newjob_observer = Observer()
    newjob_observer.schedule(file_handler.NewJob(control.proc_queue), control.proc_dir)
    control.observers.append(newjob_observer)
    newjob_observer.start()
    reprint_observer = Observer()
    reprint_observer.schedule(file_handler.Reprint(control.proc_queue), control.proc_dir)
    control.observers.append(reprint_observer)
    reprint_observer.start()
    complete_observer = Observer()
    complete_observer.schedule(file_handler.Completed(control.proc_queue), control.proc_dir)
    control.observers.append(complete_observer)
    complete_observer.start()

    # Web setup
    control.clients = aptinterface.cl
    web_thread = threading.Thread(target=init_web_server, args=(control.sysconf['HTTPServer']['host'],
                                                                control.sysconf['HTTPServer']['port']))
    web_thread.start()

    return control

