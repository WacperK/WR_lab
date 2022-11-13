#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_4, INPUT_1
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.led import Leds

# TODO: Add code here

#wheels = MoveTank(OUTPUT_C, OUTPUT_A)

SENSOR_MIDDLE = 17 	#wartość odbicia 50/50 na czarnej linii
SENSOR_LEFT = 8 	#czujnik skrecajacy w linie
SENSOR_RIGHT = 30	#czujnik poza linią


try:
	print("Definicja stalych")
	#wheels.on_for_rotations(SpeedPercent(10), SpeedPercent(10), 10



	print("Przypisywanie czujnikow")
	# !!!!!!!!!!!ZMIEN PRZYPISANIE CZUJNIKOW ( W MODULACH TEZ ) !!!!!!!!!!!!!!


	class Senses:
		def __init__(self):
			self.leftSensor = ColorSensor(INPUT_4)
			self.rightSensor = ColorSensor(INPUT_1)
			self.rightReadout = 0
			self.leftReadout = 0
			self.lastRightReadout = 0
			self.lastLeftReadout = 0
			self.alertValue = 28

		def readR(self):
			temp = self.rightSensor.reflected_light_intensity
			self.lastRightReadout = rightReadout
			self.rightReadout = temp
			return temp

		def readL(self):
			temp = self.leftSensor.reflected_light_intensity
			self.lastLeftReadout = leftReadout
			self.leftReadout = temp
			return temp

		def lVal(self):
			return self.leftReadout

		def rVal(self):
			return self.rightReadout

		def readout(self):
			self.readL()
			self.readR()

		def leftIsCrossing(self):
			if lVal() <= self.alertValue:
				return True:
			else:
				return False:

		def rightIsCrossing(self):
			if rVal() <= self.alertValue:
				return True:
			else:
				return False:
		'''
		def isCrossing(self):
			parameters = {}
			parameters['left'] = leftIsCrossing()
			parameters['right'] = rightIsCrossing()
			return parameters 
		'''



	print("Definicja klasy kolek")
	class Wheels:
		def __init__(self, reverseWheels=False):
			#obrocenie dzialania silnikow
			if reverseWheels==False:
				self.polarity = 'normal'
			else:
				self.polarity = 'inversed'
			self.leftMotor = LargeMotor(OUTPUT_A, polarity=self.polarity)
			self.rightMotor = LargeMotor(OUTPUT_C, polarity=self.polarity)
			#Wartosci dodawane do silnika
			self.rightAdd = 0
			self.leftAdd = 0
			self.maxTurnAdd = 10
			self.normalSpeed = 20

		def setWheels(self, speedLeft, speedRight):
			if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
				print(f"Zla wartosc na silniku. L{speedLeft}; R{speedRight}")
				return

			self.leftMotor.on(SpeedPercent(speedLeft))
			self.rightMotor.on(SpeedPercent(speedLeft))

		
		#Docelowa funkcja sterujaca(predkosc normalna+przyrosty)
		def drive(self):
			setWheels(self.normalSpeed + self.leftAdd, self.normalSpeed + self.rightAdd)

		#Czy skreca?
		def isTurning(self):
			if self.rightAdd==0 and self.leftAdd==0:
				return False:
			else:
				return True

		#zmiana wartosci delty predkosci
		def changeLAdd(self, value):
			if value > self.maxTurnAdd:
				return
			else:
				leftAdd = value

		def changeLAdd(self, value):
			if value > self.maxTurnAdd:
				return
			else:
				leftAdd = value


	print("Inicjalizacja sensorow oraz silnikow")
	motors = Wheels(False)
	sense = Senses()

	print('Entering the loop...')
	#Glowna petla
	while(1):
		sense.readout()
		motors.drive()

except KeyboardInterrupt: #ctrl+c
	try:
		motors.setWheels(0,0)
	except:
		pass

	print("Program zakończony przez użytkownika")
			
			
		
