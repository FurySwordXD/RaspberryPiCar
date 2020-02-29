#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER_1 = 18
GPIO_ECHO_1 = 24

GPIO_TRIGGER_2 = 22
GPIO_ECHO_2 = 27
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)
 
def distance(trigger, echo):
    # set Trigger to HIGH
    GPIO.output(trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trigger, False)
 
    StartTime = time.time()
    StopTime = time.time()
    
    print("Waiting Echo...")
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
    
    print("Calculating...")
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
            print ("1. Measured Distance = %.1f cm" % dist)

            dist = distance(GPIO_TRIGGER_2, GPIO_ECHO_2)
            print ("2. Measured Distance = %.1f cm" % dist)
            
            print("")
            time.sleep(3)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()