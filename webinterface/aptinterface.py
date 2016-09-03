import socket
import json
from flask import Flask, render_template
from logging_setup import init_logging

logger = init_logging()

app = Flask(__name__)

TCP_IP = '127.0.0.1'
TCP_PORT = 8091


def send_demo_control(in_data):
    message = ['demo control', in_data]
    output = json.dumps(message)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.sendall(output.encode('utf-8'))
    s.close()


@app.route('/')
def index():
    return render_template('demo_controller.html')


@app.route('/demo_controller')
def demo_controls():
    return render_template('demo_controller.html')


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
