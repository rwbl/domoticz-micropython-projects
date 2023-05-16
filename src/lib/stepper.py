"""
File: stepper.py
Date: 20230506
Author: Robert W.B. Linn
:description
Library for the stepper motor 8BYJ-48 5V DC with ULN2003 motor driver.
Tested on a Raspberry Pi Pico W.
:credits
This library is based upon the Micropython code to drive stepper motors via ULN2003 with the BBC micro:bit.
https://github.com/IDWizard/uln2003 (c) IDWizard 2017, # MIT License. Thanks for developing & sharing.
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
    # The number of steps for a full rotation. Between 508-509 steps for one revolution.
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
        """
        Init the class with default Pico pins GP2 - GP5.
        
        :param stepmode string
            Set the stepmode to HALF_STEP_MODE or FULL_STEP_MODE
            
        :param IN1 - IN4 int
            Set the 4 stepper motor pin numbers.
            The defaults are the Raspberry Pico pins GP2 (Pin #4) - GP5 (Pin #7).
            
        :param delay int
            Set the step move delay in ms.
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
 
        # Initialize all pins to 0
        self.reset()
 
    def step(self, count, direction=1):
        """
        Move the stepper by steps.
        
        :param count int
            Set the number of steps to move.
            If count == -1 then direction is anti-clockwise.
            
        :param direction int
            Set the stepper motor move direction.
            Directions: clockwise (cw) = 1, anti-clockwise (acw) = -1
        """
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
        """
        Move the stepper by angle.
        
        :param angle int
            Set the angle to move the stepper motor.
            If r < 0 then direction is anti-clockwise.
            
        :param direction int
            Set the stepper motor move direction.
            Directions: clockwise (cw) = 1, anti-clockwise (acw) = -1
        """
        if r < 0:
            direction = -1
            r = abs(r)
    	self.step(int(self.FULL_ROTATION * r / 360), direction)
    def rotate(self, count, direction=1):
        """
        Rotate the stepper by 360°.
        
        :param count int
            Set the number of rotations to move.
            If count == -1 then direction is anti-clockwise.
            
        :param direction int
            Set the stepper motor move direction.
            Directions: clockwise (cw) = 1, anti-clockwise (acw) = -1
        """
        if count < 0:
            direction = -1
            count = abs(count)
        for n in range(count):
            self.angle(360, direction)
    def reset(self):
        """
        Reset to the stepper motor pins to 0.
        There is no holding, the pins are geared, not movevable.
        """
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
