#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_4, INPUT_3
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.led import Leds

# TODO: Add code here

#wheels = MoveTank(OUTPUT_C, OUTPUT_A)

try:
	print("Definicja stalych")
	#wheels.on_for_rotations(SpeedPercent(10), SpeedPercent(10), 10



	print("Przypisywanie czujnikow")
	# !!!!!!!!!!!ZMIEN PRZYPISANIE CZUJNIKOW ( W MODULACH TEZ ) !!!!!!!!!!!!!!


	class Senses:
		def __init__(self):
			self.leftSensor = ColorSensor(INPUT_3)
			self.rightSensor = ColorSensor(INPUT_4)
			self.rightReadout = 0
			self.leftReadout = 0
			self.lastRightReadout = 0
			self.lastLeftReadout = 0
			self.alertValue = 28
			self.lNormalValue = 35
			self.rNormalValue = 28
			self.errorTrigger = 8
			self.leftAlert = self.lNormalValue - self.errorTrigger
			self.rightAlert =  self.rNormalValue - self.errorTrigger

		def readR(self):
			temp = self.rightSensor.reflected_light_intensity
			self.lastRightReadout = self.rightReadout
			self.rightReadout = temp
			return temp

		def readL(self):
			temp = self.leftSensor.reflected_light_intensity
			self.lastLeftReadout = self.leftReadout
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
			if self.lVal() <= self.leftAlert:
				return True
			else:
				return False

		def rightIsCrossing(self):
			if self.rVal() <= self.rightAlert:
				return True
			else:
				return False
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
			self.leftMotor = LargeMotor(OUTPUT_A)
			self.rightMotor = LargeMotor(OUTPUT_C)
			self.leftMotor.polarity=self.polarity
			self.rightMotor.polarity=self.polarity
			#Wartosci dodawane do silnika
			self.rightAdd = 0
			self.leftAdd = 0
			self.maxTurnAdd = 10
			self.normalSpeed = 20

		def setWheels(self, speedLeft, speedRight):
			if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
				print("Zla wartosc na silniku.")
				print(speedLeft, speedRight)
				return

			self.leftMotor.on(SpeedPercent(speedLeft))
			self.rightMotor.on(SpeedPercent(speedRight))

		
		#Docelowa funkcja sterujaca(predkosc normalna+przyrosty)
		def drive(self):
			self.setWheels(self.normalSpeed + self.leftAdd, self.normalSpeed + self.rightAdd)

		#Czy skreca?
		def isTurning(self):
			if self.rightAdd==0 and self.leftAdd==0:
				return False
			else:
				return True

		#zmiana wartosci delty predkosci
		def changeLAdd(self, value):
			if value > self.maxTurnAdd:
				return
			else:
				self.leftAdd = value

		def changeRAdd(self, value):
			if value > self.maxTurnAdd:
				return
			else:
				self.rightAdd = value
		
		def turnRight(self):
			self.rightAdd = -10
			self.leftAdd = 5

		def turnLeft(self):
			self.leftAdd = -10
			self.rightAdd = 5

		def clearAdd(self):
			self.rightAdd = 0
			self.leftAdd = 0



	print("Inicjalizacja sensorow oraz silnikow")
	motors = Wheels(True)
	sense = Senses()

	print('Entering the loop...')
	#Glowna petla
	while(1):
		sense.readout()
		if sense.rightIsCrossing() or sense.leftIsCrossing():
			if sense.rightIsCrossing() and sense.leftIsCrossing():
				print('Skrzyzowanie')
				motors.clearAdd()
			elif sense.leftIsCrossing():
				print('Skrecam w lewo')
				motors.turnRight()
			elif sense.rightIsCrossing():
				print('Skrecam w prawo')
				motors.turnLeft()

		else:
			motors.clearAdd
			print('Prosto')


		print(sense.lVal(), sense.rVal())	
		motors.drive()
		
except KeyboardInterrupt: #ctrl+c
	try:
		motors.setWheels(0,0)
	except:
		pass

	print("Program zakonczony przez uzytkownika")
			
			
		
