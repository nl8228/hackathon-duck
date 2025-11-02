#from alarm import Alarm
import time
import sys
import RPi.GPIO as GPIO
import requests

SERVO_PIN = 11
BUTTON_PIN = 7

def timer(seconds): 
    min = 0
    sec = 0
    while seconds >= 0:
        min = seconds // 60
        sec = seconds % 60
        time.sleep(1)
        seconds -= 1


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#servo setup
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN,50)

#button setup
GPIO.setup(BUTTON_PIN, GPIO.IN)

alarm_triggered = False

def angle_to_duty(angle):
    return 2 + (angle/18)

#triggers the servo so open
def trigger_servo():
    print("alarm triggered, move servo")
    pwm.start(0)
    global alarm_triggered
    alarm_triggered = True
    duty_cycle = angle_to_duty(30)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    while (GPIO.input(BUTTON_PIN) == 0):
        time.sleep(0.01)

    print("button pressed")
    stop_alarm()
    

def stop_alarm():
    requests.post("http://127.0.0.1:8000/api/go-home", timeout=1)
    print("Sent go-home signal")
    pwm.ChangeDutyCycle(0)
    time.sleep(0.5)
    pwm.stop()


