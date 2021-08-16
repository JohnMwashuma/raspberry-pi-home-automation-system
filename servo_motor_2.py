# Import libraries
import RPi.GPIO as GPIO
import time

def spin_motor(spin=True):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    servo_pin = 27
    GPIO.setup(servo_pin, GPIO.OUT)
    pwd = GPIO.PWM(servo_pin, 50)
    pwd.start(0)
    print('>>>>>I WAS HERE!!!!')
    while (spin):
        for i in range(0, 180):
            DC = 1./18.*(i) + 2
            pwd.ChangeDutyCycle(DC)
            time.sleep(0.02)
        for i in range(180, 0, -1):
            DC = 1./18.*(i) + 2
            pwd.ChangeDutyCycle(DC)
            time.sleep(0.02)
    pwd.stop()
    GPIO.cleanup()

# # Set GPIO numbering mode
# GPIO.setmode(GPIO.BOARD)

# # Set pin 13 as an output, and set pwd as pin 13 as PWM
# servo_pin = 13
# GPIO.setup(servo_pin,GPIO.OUT)
# pwd = GPIO.PWM(servo_pin,50) # Note 13 is pin, 50 = 50Hz pulse

# #start PWM running, but with value of 0 (pulse off)
# pwd.start(0)

# # Loop for duty values from 2 to 12 (0 to 180 degrees)
# while True:
#     for i in range(0, 180):
#       DC = 1./18.*(i) + 2
#       pwd.ChangeDutyCycle(DC)
#       time.sleep(0.02)
#     for i in range(180, 0, -1):
#       DC = 1./18.*(i) + 2
#       pwd.ChangeDutyCycle(DC)
#       time.sleep(0.02)


# #Clean things up at the end
# pwd.stop()
# GPIO.cleanup()
spin_motor()
print ("Goodbye")
