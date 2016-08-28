__author__ = 'Syn'
import threading
from config import DEF_DEMO_CONF
from config import DEF_JIF_CONF
from controller import DemoController
from logging_setup import init_logging
from dispatcher import Dispatcher
from watchdog.observers import Observer
from folder_monitor import folder_monitor_handler as fmh

logger = init_logging()


def init_controller():
    control = DemoController(DEF_DEMO_CONF, DEF_JIF_CONF)
    control.lock = threading.Lock()
    control.dispatcher = Dispatcher(control)
    control.dispatcher.start()

    logger.boot('Starting jif monitor.')
    jifack = Observer()
    jifack.schedule(fmh.JIFAckHandler(control.command_queue, control.lock),
                    path=DEF_DEMO_CONF[1]['APTDirs']['JIFACK'])
    jifack.start()
    control.observers.append(jifack)
    logger.boot('Starting reprint monitor.')
    reprintmon = Observer()
    reprintmon.schedule(fmh.ReprintHandler(control.command_queue, control.lock),
                        path=DEF_DEMO_CONF[1]['APTDirs']['REPRINT'])
    reprintmon.start()
    control.observers.append(reprintmon)
    logger.boot('Starting proc change monitor.')
    proc_mon = Observer()
    proc_mon.schedule(fmh.ProcChangeManager(control.command_queue, control.lock),
                      path=DEF_DEMO_CONF[1]['APTDirs']['PROC'])
    proc_mon.start()
    control.observers.append(proc_mon)
    logger.boot('Monitors initialized.')
    return control

