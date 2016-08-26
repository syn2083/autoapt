__author__ = 'Syn'
import os


BASE_DIR = os.getcwd()

# Logger Configs
log_dir = os.path.join(BASE_DIR, 'logs')
log_file = os.path.join(log_dir, 'aptdemo.log')

# Socket Server Configs
SERV_ADDR = '127.0.0.1'
SOCK_PORT = 8091
CHUNK_SIZE = 4096
