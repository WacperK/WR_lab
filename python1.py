#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_4, INPUT_3
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.led import Leds
from time import sleep

# TODO: Add code here


try:

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
			self.errorTrigger = 15
			#self.leftAlert = self.lNormalValue - self.errorTrigger
			#self.rightAlert =  self.rNormalValue - self.errorTrigger
			self.leftAlert = 15
			self.rightAlert = 15

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

		def lostLine(self):
			if self.rVal() > 30 and self.lVal() > 35:
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
	

	class ErrorHandler:
		def __init__(self, sense):
			self.sense = sense
			self.lError = 0
			self.rError = 0
			self.lastLError = 0
			self.lastRError = 0
			#Parametry regulatora
			self.proportional = 0.3
			self.differential = 0
			#Korekcje
			self.rCorrection = 0
			self.lCorrection = 0
			self.lIntegral = 0
			self.rIntegral = 0
			#Korekcje skumulowane
			

			
		def calcRCorrection(self):
			self.rCorrection = self.rError * self.proportional


		def calcLCorrection(self):
			self.lCorrection = self.lError * self.proportional

		def incLIntegral(self):
			self.lIntegral+=1

		def incRIntegral(self):
			self.rIntegral+=1

		def clearRIntegral(self):
			self.rIntegral = 0

		def clearLIntegral(self):
			self.lIntegral = 0

		def updateValues(self):
			self.lastLError = self.lError
			self.lastRError = self.rError
			if sense.lVal() <= sense.leftAlert:
				self.lError = sense.leftAlert - sense.lVal()
			else:
				self.lError = 0

			if sense.rVal() <= sense.rightAlert:
				self.rError = sense.rightAlert - sense.rVal()
			else:
				self.rError = 0
			#self.lError = self.sense.lNormalValue -  self.sense.leftReadout
			#self.rError = self.sense.rNormalValue - self.sense.rightReadout	
			self.calcRCorrection()
			self.calcLCorrection()

		def returnLIntegral():
			if self.lIntegral <= 20:
				return int(self.lIntegral)
			else:
				return 20

		def returnRIntegral():
			if self.rIntegral <= 20:
				return int(self.rIntegral)
			else:
				return 20
		
		def returnLCorr(self):
			return int(self.lCorrection)

		def returnRCorr(self):
			return int(self.rCorrection)
			
			
			

	print("Definicja klasy kolek")
	class Wheels:
		def __init__(self, reverseWheels=False, errorHandler=None):
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
			self.normalSpeed = 12
			self.lastTurn = '0'
			#ErrorHandler
			self.error = errorHandler

		def setWheels(self, speedLeft, speedRight):
			#check wartosci, czy nie przekroczono wartosci maksymalnych
			if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
				print("Zla wartosc na silniku.")
				print(speedLeft, speedRight)
				return

			#odpalenie silnikow

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

		def isTurningRight(self):
			if self.leftAdd > 0 or self.error.lIntegral > 0:
				return True
			else:
				return False

		def isTurningLeft(self):
			if self.rightAdd > 0 or self.error.rIntegral > 0:
				return True
			else:
				return False


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
			self.rightAdd = self.error.returnRCorr()
			self.leftAdd = -20
			self.lastTurn = 'r'

		def turnLeft(self):
			self.leftAdd = self.error.returnLCorr()
			self.rightAdd = -20
			self.lastTurn = 'l' 

		def clearAdd(self):
			self.rightAdd = 0
			self.leftAdd = 0 

		def setNormalSpeed(self, speed):
			self.normalSpeed = speed

		def checkLine(self):
			if self.error.sense.lostLine():
				self.setNormalSpeed(0)

			else:
			 	self.setNormalSpeed(20)
			



	print("Inicjalizacja sensorow oraz silnikow")
	sense = Senses()
	errHandler  = ErrorHandler(sense)
	motors = Wheels(True, errHandler)
	

	print('Entering the loop...')
	#Glowna petla
	while(1):

		sense.readout()
		errHandler.updateValues()
		
		if sense.rightIsCrossing() or sense.leftIsCrossing() or sense.lostLine():
			if sense.rightIsCrossing() and sense.leftIsCrossing():
				print('Skrzyzowanie')
				motors.clearAdd()
			elif sense.leftIsCrossing():
				print('Skrecam w lewo')
				motors.checkLine()
				motors.turnLeft()
			elif sense.rightIsCrossing():
				print('Skrecam w prawo')
				motors.checkLine()
				motors.turnRight()
			elif sense.lostLine():
				if motors.lastTurn == 'r':
					motors.turnRight()
				elif motors.lastTurn == 'l':
					motors.turnLeft()
				else:
					pass

		elif(sense.lostLine()):
			print("Linia Zgubiona")
			if motors.lastTurn =='r':
				motors.turnRight()
			elif motors.lastTurn == 'l':
				motors.turnLeft()
		else:
			motors.clearAdd()
			errHandler.clearRIntegral()
			errHandler.clearLIntegral()
			print('Prosto')
		
		motors.drive()
		
		#print(sense.lVal(), sense.rVal())		
		print(sense.lVal(), sense.rVal())	
		
		
except KeyboardInterrupt: #ctrl+c
	try:
		motors.setWheels(0,0)
	except:
		pass

	print("Program zakonczony przez uzytkownika")
			
			
		
