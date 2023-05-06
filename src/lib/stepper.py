"""
File: stepper.py
Date: 20230429
Author: https://github.com/IDWizard/uln2003 (c) IDWizard 2017, # MIT License. Thanks for developing & sharing.
Enhanced: Robert W.B. Linn
Library for the stepper motor 8BYJ-48 5V DC with ULN2003 motor driver.
Tested on a Raspberry Pi Pico W.
:usage
stepper = Stepper('HALF_STEP',2 , 3, 4, 5, delay=1)
stepper.step(60, 1)
time.sleep(1)
stepper.step(-60)
time.sleep(1)
stepper.angle(90, 1)
time.sleep(1)
stepper.angle(-90)
time.sleep(1)
stepper.rotate(1)
time.sleep(1)
stepper.rotate(-1)
time.sleep(1)
"""
# Imports
from machine import Pin
import time
 
# 
class Stepper:
    # Reference: http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html
    FULL_ROTATION = int(4075.7728395061727 / 8)
    # Modes
    HALF_STEP_MODE = 'HALF_STEP'
    FULL_STEP_MODE = 'FULL_STEP'
    # Mode bit sequences for the 4 motor pins
    HALF_STEP = [
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 1],
    ]
 
    FULL_STEP = [
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1]
    ]
    def __init__(self, mode=HALF_STEP_MODE, IN1=2, IN2=3, IN3=4, IN4=5, delay=1):
        """Init the class with default Pico pins GP2 - GP5.
        """
        if mode == self.FULL_STEP_MODE:
        	self.mode = self.FULL_STEP
        else:
        	self.mode = self.HALF_STEP
        self.pin1 = Pin(IN1, Pin.OUT)
        self.pin2 = Pin(IN2, Pin.OUT)
        self.pin3 = Pin(IN3, Pin.OUT)
        self.pin4 = Pin(IN4, Pin.OUT)
        # Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP
        self.delay = delay
 
        # Initialize all to 0
        self.reset()
 
    def step(self, count, direction=1):
        """Rotate count steps. direction = -1 means anti-clockwise"""
        if count < 0:
            direction = -1
            count = abs(count)
        for x in range(count):
            for bit in self.mode[::direction]:
                self.pin1(bit[0])
                self.pin2(bit[1])
                self.pin3(bit[2])
                self.pin4(bit[3])
                time.sleep_ms(self.delay)
        self.reset()
    def angle(self, r, direction=1):
        """Move the stepper by angle."""
        if r < 0:
            direction = -1
            r = abs(r)
    	self.step(int(self.FULL_ROTATION * r / 360), direction)
    def rotate(self, count, direction=1):
        """Rotate the stepper by 360°."""
        if count < 0:
            direction = -1
            count = abs(count)
        for n in range(count):
            self.angle(360, direction)
    def reset(self):
        # Reset to 0, no holding, these are geared, you can't move them
        self.pin1(0) 
        self.pin2(0) 
        self.pin3(0) 
        self.pin4(0)
"""
stepper = Stepper('HALF_STEP',2 , 3, 4, 5, delay=1)
stepper.step(60, 1)
time.sleep(1)
stepper.step(-60)
time.sleep(1)
stepper.angle(90, 1)
time.sleep(1)
stepper.angle(-90)
time.sleep(1)
stepper.rotate(1)
time.sleep(1)
stepper.rotate(-1)
time.sleep(1)
"""
