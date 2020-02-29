import sys
import time
import atexit
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

import RPi.GPIO as GPIO

app = Flask(__name__, static_url_path='/static/')
app.config['SECRET_KEY'] = 'Secret'
socket_io = SocketIO(app)

class RPICar:

    def __init__(self):
        self.left_wheels_forward = 26
        self.left_wheels_reverse = 19
        self.right_wheels_forward = 13
        self.right_wheels_reverse = 6

        self.data = {
            'forward': 0,
            'right': 0,
            'left': 0,
            'reverse': 0
        }

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.left_wheels_forward, GPIO.OUT)
        GPIO.setup(self.left_wheels_reverse, GPIO.OUT)
        GPIO.setup(self.right_wheels_forward, GPIO.OUT)
        GPIO.setup(self.right_wheels_reverse, GPIO.OUT)

        atexit.register(self.end)

    def end(self):
        GPIO.cleanup()

    def reset_data(self):
        for k in self.data.keys():
            self.data[k] = 0

    def set_data(self, key, value):
        self.reset_data()
        self.data[key] = value
        self.move()

    def move(self):
        GPIO.output(self.left_wheels_forward, GPIO.LOW)
        GPIO.output(self.left_wheels_reverse, GPIO.LOW)
        GPIO.output(self.right_wheels_forward, GPIO.LOW)
        GPIO.output(self.right_wheels_reverse, GPIO.LOW)

        if self.data['forward'] == 1:
            GPIO.output(self.left_wheels_forward, GPIO.HIGH)
            GPIO.output(self.right_wheels_forward, GPIO.HIGH)

        elif self.data['right'] == 1:
            GPIO.output(self.left_wheels_forward, GPIO.HIGH)

        elif self.data['left'] == 1:
            GPIO.output(self.right_wheels_forward, GPIO.HIGH)

        elif self.data['reverse'] == 1:
            GPIO.output(self.left_wheels_reverse, GPIO.HIGH)
            GPIO.output(self.right_wheels_reverse, GPIO.HIGH)



rpi = RPICar()

@socket_io.on('message')
def on_message(msg):
    print(msg)

@socket_io.on('connect')
def on_connect():
    print("Connected")
    emit('move', rpi.data, broadcast=True)

@socket_io.on('move')
def on_move(req_data):
    print(req_data)
    rpi.set_data(req_data['direction'], req_data['value'])
    emit('move', rpi.data, broadcast=True)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socket_io.run(app, host='0.0.0.0', port=5000, debug=False)