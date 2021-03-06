import socket
import json
import uuid
from flask import Flask, render_template
from tornado import websocket
from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler
from logging_setup import init_logging

logger = init_logging()

app = Flask(__name__)

TCP_IP = '127.0.0.1'
TCP_PORT = 8091

cl = {}


def send_demo_control(in_data, target=None):
    if in_data == 'status_check':
        message = ['demo status', in_data, target]
        output = json.dumps(message)
    else:
        message = ['demo control', in_data]
        output = json.dumps(message)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.sendall(output.encode('utf-8'))
    s.close()


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        new_id = uuid.uuid4()
        self.id = new_id.urn
        if self.id not in cl.keys():
            cl[self.id] = self
        self.ping(b'nonsense')

    def on_close(self):
        if self.id in cl.keys():
            del cl[self.id]

    def on_message(self, message):
        # logger.debug(type(message))
        if message == 'status_check':
            send_demo_control('status_check', self.id)
        logger.debug('Message from: {}, {}'.format(self.id, message))


@app.route('/')
def index():
    return render_template('demo_controller.html', control=0)


@app.route('/demo_controller')
def demo_controls():
    return render_template('demo_controller.html', control=0)


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/start_demo/')
def start_demo():
    send_demo_control('start')
    return 'Sent Start Demo Request!'


@app.route('/stop_demo/')
def stop_demo():
    send_demo_control('stop')
    return 'Sent Stop Demo Request!'


@app.route('/pause_demo/')
def pause_demo():
    send_demo_control('pause')
    return 'Sent Pause Demo Request!'


@app.route('/reset_seed/')
def reset_seed():
    send_demo_control('reset_seed')
    return 'Sent Reset Seed Request!'


@app.route('/status_check/')
def status_check():
    send_demo_control('status_check')
    return 'Status Checking'

container = WSGIContainer(app)
server = Application([(r'/ws', SocketHandler), (r'.*', FallbackHandler, dict(fallback=container))])
