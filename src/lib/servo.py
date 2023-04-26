"""
File:	servo.py
Date:	20230305
Author:	Robert W.B. Linn
:description
Class control a servo motor.
Tested with a Tower Pro Micro Servo 9 g SG90.
Min and max duty default values are obtained via try out.
Min angle is 0, max angle is 180.
Servo signal pin is default Pico Pin GP0 (Pin #1).
"""
# Imports
import machine
from machine import Pin, PWM
# Servo Class
class Servo:
    """
    Init the servo with defaults.
    
    :parameter long MIN_DUTY
    :parameter long MAX_DUTY
    
    :parameter int pin
    
    :parameter int frequency
    """
    def __init__(self, MIN_DUTY=500000, MAX_DUTY=2500000, pin=0, frequency=50):
        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(frequency)
        self.MIN_DUTY = MIN_DUTY
        self.MAX_DUTY = MAX_DUTY
        
    """
    Set the servo angle between 0 - 180 degrees.
    
    :parameter int angle
        Set the angle of the servo between 0 - 180 degrees.
    :return flat duty_ns
    """
    def setAngle(self, angle):
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        duty_ns = int(self.MAX_DUTY - angle * (self.MAX_DUTY-self.MIN_DUTY)/180)
        # print(duty_ns)
        self.pwm.duty_ns(duty_ns)
        return duty_ns
