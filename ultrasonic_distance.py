#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_1 = 14
GPIO_ECHO_1 = 15

GPIO_TRIGGER_2 = 22
GPIO_ECHO_2 = 27
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)

maxTime = 0.04

def calculate_distance(trigger, echo):
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
 
if __name__ == '__main__':
    try:
        while True:
            dist = calcuate_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
            print ("1. Measured Distance = %.1f cm" % dist)

            dist = calcuate_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)
            print ("2. Measured Distance = %.1f cm" % dist)
            
            print("")
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()