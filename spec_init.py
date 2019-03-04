# initialize serial port for od600 readings
# available for both windows and linux

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 04 11:38:42 2019

@author: A
"""
from serial import Serial
import os

if os.name == 'posix':
    spec = Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
elif os.name == 'nt':
    spec = Serial('COM3', baudrate=9600, timeout=1) # COM3 for closest left usb port
spec.write('a\n')
spec.write('K0\n')
print spec.readlines()
spec.close()

if os.name == 'posix':
    spec2 = Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
elif os.name == 'nt':
    spec2 = Serial('COM3', baudrate=115200, timeout=1)
spec2.write('a\n')
print spec2.readlines()
spec2.close()