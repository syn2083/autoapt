__author__ = 'Syn'
import os
import sys

BASE_DIR = os.getcwd()

# Logger Configs
log_dir = os.path.join(BASE_DIR, 'logs')
log_file = os.path.join(log_dir, 'aptdemo.log')

# Socket Server Configs
SERV_ADDR = '127.0.0.1'
SOCK_PORT = 8091
CHUNK_SIZE = 4096

# System Configs
DEMO_CONF_DIR = os.path.join(os.getcwd(), '\\config_files')
DEMO_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'demo.config')
JIF_CONF_FILE = os.path.join(DEMO_CONF_DIR, 'jif.config')

def init_configs():
    if not os.path.exists(DEMO_CONF_DIR):
        os.makedirs(DEMO_CONF_DIR)
