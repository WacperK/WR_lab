#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.led import Leds

# TODO: Add code here

wheels = MoveTank(OUTPUT_C, OUTPUT_A)

#wheels.on_for_rotations(SpeedPercent(10), SpeedPercent(10), 10)

text = 'some text'

sensor = ColorSensor(INPUT_4)

SENSOR_MIDDLE = 17

SENSOR_LEFT = 8

SENSOR_RIGHT = 30

print('Some text')
while(1):
	print(sensor.reflected_light_intensity)	
		
	
