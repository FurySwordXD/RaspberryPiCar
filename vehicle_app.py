import sys
import time
import RPi.GPIO as GPIO
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__, static_url_path='/static/')
app.config['SECRET_KEY'] = 'Secret'
socket_io = SocketIO(app)

def end():
    GPIO.cleanup()

import atexit
atexit.register(end)

left_wheels = 26
right_wheels = 6
sleeptime = 1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_wheels, GPIO.OUT)
GPIO.setup(right_wheels, GPIO.OUT)

data = {
    'forward': 0,
    'right': 0,
    'left': 0
}

def reset_data():
    for k in data.keys():
        data[k] = 0

def set_data(key, value):
    reset_data()
    data[key] = value
    move()

def move():
    GPIO.output(left_wheels, GPIO.LOW)
    GPIO.output(right_wheels, GPIO.LOW)

    if data['forward'] == 1:
        GPIO.output(left_wheels, GPIO.HIGH)
        GPIO.output(right_wheels, GPIO.HIGH)

    elif data['right'] == 1:
        GPIO.output(right_wheels, GPIO.HIGH)

    elif data['left'] == 1:
        GPIO.output(left_wheels, GPIO.HIGH)


@socket_io.on('message')
def on_message(msg):
    print(msg)

@socket_io.on('connect')
def on_connect():
    print("Connected")
    emit('move', data, broadcast=True)

@socket_io.on('move')
def on_move(req_data):
    print(req_data)
    set_data(req_data['direction'], req_data['value'])
    emit('move', data, broadcast=True)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socket_io.run(app, host='0.0.0.0', port=5000, debug=False)