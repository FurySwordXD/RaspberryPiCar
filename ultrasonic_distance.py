#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_1 = 17
GPIO_ECHO_1 = 22

# GPIO_TRIGGER_2 = 22
# GPIO_ECHO_2 = 27

# GPIO_TRIGGER_3 = 12
# GPIO_ECHO_3 = 16
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)

# GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
# GPIO.setup(GPIO_ECHO_2, GPIO.IN)


# GPIO.setup(GPIO_TRIGGER_3, GPIO.OUT)
# GPIO.setup(GPIO_ECHO_3, GPIO.IN)

maxTime = 0.04

def calculate_distance(trigger, echo):
    maxTime = 0.04

    GPIO.output(trigger, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(trigger, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger, GPIO.LOW)

    success = True
    pulse_start = time.time()
    timeout = pulse_start + maxTime
    while GPIO.input(echo) == 0:
        if pulse_start< timeout:
            pulse_start = time.time()
        else:
            return 0

    pulse_end = time.time()
    timeout = pulse_end + maxTime
    while GPIO.input(echo) == 1:
        if pulse_end < timeout:
            pulse_end = time.time()
        else:
            return 0

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17000
    distance = round(distance, 2)

    return distance
 
if __name__ == '__main__':
    try:
        while True:
            d1 = calculate_distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
            print ("1. Measured Distance = %.1f cm" % d1)

            # d2 = calculate_distance(GPIO_TRIGGER_2, GPIO_ECHO_2)
            # print ("2. Measured Distance = %.1f cm" % d2)

            # d3 = calculate_distance(GPIO_TRIGGER_3, GPIO_ECHO_3)
            # print ("3. Measured Distance = %.1f cm" % d3)
            
            print("")
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()