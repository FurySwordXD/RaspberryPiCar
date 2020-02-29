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
enable_a = 21
enable_b = 20
sleeptime = 1


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_wheels, GPIO.OUT)
GPIO.setup(right_wheels, GPIO.OUT)
GPIO.setup(enable_a, GPIO.OUT)
GPIO.setup(enable_b, GPIO.OUT)

p1 = GPIO.PWM(enable_a, 1000)
p2 = GPIO.PWM(enable_b, 1000)
p1.start(50)
p2.start(50)

def rotate_left(x):
    GPIO.output(left_wheels, GPIO.HIGH)
    print("Moving Left")
    time.sleep(x)
    GPIO.output(left_wheels, GPIO.LOW)
    time.sleep(x)

def rotate_right(x):
    GPIO.output(right_wheels, GPIO.HIGH)
    print("Moving Right")
    time.sleep(x)
    GPIO.output(right_wheels, GPIO.LOW)

while (1):
    speed = int(input("Enter speed (0-100): ").strip())
    p1.ChangeDutyCycle(speed)
    p2.ChangeDutyCycle(speed)
    rotate_left(sleeptime)
    rotate_right(sleeptime)
    #time.sleep(sleeptime)