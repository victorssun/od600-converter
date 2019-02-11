#!/usr/bin/env python
from serial import Serial

spec = Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
spec.write('a\n')
spec.write('K0\n')
print spec.readlines()
spec.close()

spec2 = Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
spec2.write('a\n')
print spec2.readlines()
spec2.close()