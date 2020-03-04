import sys
import time
import atexit
import json
import math
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit
from threading import Thread
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
        
        self.enable_a = 21
        self.enable_b= 20

        self.trigger_1 = 14
        self.echo_1 = 15
        self.trigger_2 = 22
        self.echo_2 = 27

        self.data = {
            'movement_input': {'throttle': 0, 'steer': 0},
            'ai_input': {'throttle': 0, 'steer': 0},
            'distances': [0, 0]
        }

        self.ai_mode = False

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.left_wheels_forward, GPIO.OUT)
        GPIO.setup(self.left_wheels_reverse, GPIO.OUT)
        GPIO.setup(self.right_wheels_forward, GPIO.OUT)
        GPIO.setup(self.right_wheels_reverse, GPIO.OUT)
        
        GPIO.output(self.left_wheels_forward, GPIO.HIGH)
        GPIO.output(self.right_wheels_forward, GPIO.HIGH)

        GPIO.setup(self.enable_a, GPIO.OUT)
        GPIO.setup(self.enable_b, GPIO.OUT)

        GPIO.setup(self.trigger_1, GPIO.OUT)
        GPIO.setup(self.echo_1, GPIO.IN)
        GPIO.setup(self.trigger_2, GPIO.OUT)
        GPIO.setup(self.echo_2, GPIO.IN)

        self.left_speed = GPIO.PWM(self.enable_a, 1000)
        self.right_speed = GPIO.PWM(self.enable_b, 1000)
        self.left_speed.start(0)
        self.right_speed.start(0)

        atexit.register(self.end)

        # AI
        self.load_model()
        self.ai_thread = Thread(target=self.ai_actions, args=[])
        self.ai_thread.daemon = True
        self.ai_thread.start()

    def ai_actions(self):
        while True:
            self.think()

    def load_model(self):
        self.nodes = {}
        self.connections = {}
        self.outputs = [0, 0]

        with open('RPICarData.json') as file:
            data = json.loads(file.read())
            for node in data['Nodes']:
                self.nodes[node['id']] = node

            for con in data['Connections']:
                self.connections[con['innovationNumber']] = con

        for n in self.nodes:
            self.nodes[n]['outputValue'] = 0.0 

    def back_propagate(self, node_id):
        node = self.nodes[node_id]
        for c in self.connections:
            con = self.connections[c]
            if con['outputNode'] == node_id and con['status'] == "True":
                input_node = self.nodes[con['inputNode']]
                if input_node['type'] != "INPUT":
                    self.back_propagate(con['inputNode'])

                node['outputValue'] += input_node['outputValue'] * con['weight']

        if node['type'] != "INPUT":
            node['outputValue'] = math.tanh(node['outputValue'])

    def clamp(self, num, min_value, max_value):
        return max(min(num, max_value), min_value)

    def think(self):
        for n in self.nodes:
            self.nodes[n]['outputValue'] = 0
        
        input_2 = self.calculate_distance(self.trigger_1, self.echo_1)
        input_1 = self.calculate_distance(self.trigger_2, self.echo_2)

        self.data['distances'] = [input_1, input_2]
        self.nodes[1]['outputValue'] = self.clamp(input_1 / 400.0, 0.0, 1.0)
        self.nodes[2]['outputValue'] = self.clamp(input_2 / 400.0, 0.0, 1.0)

        output_index = 0
        for n in self.nodes:
            node = self.nodes[n]
            if node['type'] == "OUTPUT":
                self.back_propagate(node['id'])
                self.outputs[output_index] = node['outputValue']
                output_index += 1

        self.data['ai_input']['throttle'] = int(self.outputs[0] * 100) / 100.0
        self.data['ai_input']['steer'] = int(self.outputs[1] * 100) / 100.0

        if self.ai_mode:
            self.move()


    def end(self):
        GPIO.cleanup()

    def reset_data(self):
        for k in self.data.keys():
            self.data[k] = 0

    def set_data(self, movement_input):
        #self.reset_data()
        self.data['movement_input'] = movement_input
        self.move()

    def calculate_distance(self, trigger, echo):
        maxTime = 0.04

        GPIO.output(trigger,False)
        time.sleep(0.01)
        GPIO.output(trigger,True)
        time.sleep(0.00001)
        GPIO.output(trigger,False)

        pulse_start = time.time()
        timeout = pulse_start + maxTime
        while GPIO.input(echo) == 0 and pulse_start < timeout:
            pulse_start = time.time()

        pulse_end = time.time()
        timeout = pulse_end + maxTime
        while GPIO.input(echo) == 1 and pulse_end < timeout:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        distance = round(distance, 2)

        return distance

    def change_range(self, in_min, in_max, out_min, out_max, value):
        if abs(value) < 0.1:
            return 0
        return ( (value - in_min) / (in_max - in_min) ) * (out_max - out_min) + out_min

    def move(self):

        throttle = self.data['movement_input']['throttle']
        steer = self.data['movement_input']['steer']

        if self.ai_mode:
            throttle = self.data['ai_input']['throttle']
            steer = self.data['ai_input']['steer']
            
        GPIO.output(self.left_wheels_reverse, GPIO.LOW)
        GPIO.output(self.right_wheels_reverse, GPIO.LOW)
        GPIO.output(self.left_wheels_forward, GPIO.HIGH)
        GPIO.output(self.right_wheels_forward, GPIO.HIGH)

        if throttle < -0.1:
            GPIO.output(self.left_wheels_forward, GPIO.LOW)
            GPIO.output(self.right_wheels_forward, GPIO.LOW)
            GPIO.output(self.left_wheels_reverse, GPIO.HIGH)
            GPIO.output(self.right_wheels_reverse, GPIO.HIGH)

        speed_l = int(self.change_range(0, 1, 0.4, 1, abs(throttle)) * 100)
        speed_r = int(self.change_range(0, 1, 0.4, 1, abs(throttle)) * 100)

        if self.ai_mode:
            speed_l = 40
            speed_r = 40

        if abs(steer) > 0.2:
            speed_l = int(self.change_range(0, 1, 0.4, 1, abs(steer)) * 100) if steer > 0 else 0
            speed_r = int(self.change_range(0, 1, 0.4, 1, abs(steer)) * 100) if steer < 0 else 0

        #print(speed_l, speed_r)
        self.left_speed.ChangeDutyCycle(speed_l)
        self.right_speed.ChangeDutyCycle(speed_r)
            

rpi = RPICar()

@socket_io.on('message')
def on_message(msg):
    print(msg)

@socket_io.on('connect')
def on_connect():
    print("Connected")
    emit('move', rpi.data, broadcast=True)
    emit('get_data', rpi.data, broadcast=True)

@socket_io.on('toggle_mode')
def toggle_mode():
    rpi.ai_mode = not rpi.ai_mode
    #print("AI Mode: " + str(rpi.ai_mode))
    rpi.move()
    emit('toggle_mode', rpi.ai_mode, broadcast=True)

@socket_io.on('move')
def on_move(movement_input):
    #print(movement_input)
    rpi.set_data(movement_input)
    emit('move', rpi.data, broadcast=True)

@socket_io.on('get_data')
def get_data(data):
    print("Emitting")
    emit('get_data', rpi.data, broadcast=True)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socket_io.run(app, host='0.0.0.0', port=5000, debug=False)