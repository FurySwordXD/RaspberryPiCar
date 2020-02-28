import sys
import time
import RPi.GPIO as GPIO
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

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

def rotate_left(x):
    GPIO.output(left_wheels, GPIO.HIGH)
    print("Moving Left")
    time.sleep(x)
    GPIO.output(left_wheels, GPIO.LOW)

def rotate_right(x):
    GPIO.output(right_wheels, GPIO.HIGH)
    print("Moving Right")
    time.sleep(x)
    GPIO.output(right_wheels, GPIO.LOW)

while (1):
    rotate_left(sleeptime)
    rotate_right(sleeptime)

def movement():

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)    