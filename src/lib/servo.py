# servo.py
# Class control a servo motor.
# Tested with a Tower Pro Micro Servo 9 g SG90.
# Min and max duty default values are obtained via try out.
# Min angle is 0, max angle is 180.
# Servo signal pin is default Pico Pin GP0 (Pin #1).
# 20230305

import machine
from machine import Pin, PWM

class Servo:
    # Init the servo with defaults.
    def __init__(self, MIN_DUTY=500000, MAX_DUTY=2500000, pin=0, freq=50):
        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(freq)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY
        
    # Set the servo angle between 0 - 180 degrees.
    # Return duty_ns
    def setAngle(self, angle):
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        duty_ns = int(self.MAX_DUTY - angle * (self.MAX_DUTY-self.MIN_DUTY)/180)
        # print(duty_ns)
        self.pwm.duty_ns(duty_ns)
        return duty_ns

