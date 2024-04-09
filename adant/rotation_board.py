# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:08:10 2022

@author: emanuele

Rotation Board
"""


import Phidget22.Devices.Stepper

class AdantStepper(Phidget22.Devices.Stepper.Stepper):

    def __init__(self, version=1):
        super().__init__()
        # set addressing parameters to specify which channel to open (if any)
        self.version = version
        if self.version == 1:    
            self.setDeviceSerialNumber(543283)
            # Assign any event handlers you need before calling open so that no events are missed.
            # stepper0.setCurrentLimit(2)#Open your Phidgets and wait for attachment
            self.openWaitForAttachment(5000)
            self.setCurrentLimit(1.1)
            self.setAcceleration(5000)
            self.setVelocityLimit(400)
            self.setEngaged(True)
        else:
            self.setDeviceSerialNumber(267986)
            # Assign any event handlers you need before calling open so that no events are missed.
            # stepper0.setCurrentLimit(2)#Open your Phidgets and wait for attachment
            self.openWaitForAttachment(5000)
            self.setCurrentLimit(1.5)
            self.setAcceleration(5000)
            self.setVelocityLimit(102)
            self.setEngaged(True)
            
    def getAngle(self):
        return self.getPosition() * (0.9 / 16)
            
    def rotate(self, angle):
        import time
        initialPosition = self.getPosition()
        if (self.version == 1):
            count = (angle / 0.9) * 16
            print(initialPosition, "+ count:", count)
        else:
            count = (angle / 0.9) * 8
            print(initialPosition, "+ count:", count)
            

        self.setTargetPosition(initialPosition + count)
        while(self.getIsMoving()):
            time.sleep(0.5)
        if self.getPosition() == (initialPosition + count):
            return True
        else:
            return False