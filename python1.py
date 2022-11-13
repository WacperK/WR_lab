#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent, ServoMotor, MediumMotor
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
            self.lNormalValue = 12
            self.rNormalValue = 10
            self.errorTrigger = 15
            #self.leftAlert = self.lNormalValue - self.errorTrigger
            #self.rightAlert =  self.rNormalValue - self.errorTrigger
            self.leftAlert = 15
            self.rightAlert = 10
            self.hasLostLine = False

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
                self.hasLostLine = True
                return True
            else:
                self.hasLostLine = False
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
            #podrzedna klasa czujnika
            self.sense = sense
            #blad lewy prawy i ostatnie
            self.lError = 0
            self.rError = 0
            self.lastLError = 0
            self.lastRError = 0
            #Parametry regulatora
            self.proportional = 0.5
            self.differential = 0
            #Korekcje
            self.rCorrection = 0
            self.lCorrection = 0
            
        def calcRCorrection(self):
            self.rCorrection = self.rError * self.proportional


        def calcLCorrection(self):
            self.lCorrection = self.lError * self.proportional


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
            if self.rightAdd > 0:
                return True
            else:
                return False
        
        def lostLineBoost(self):
            if self.error.sense.hasLostLine == True:
                return 30
            else:
                return 0
        
        def turnRight(self):
            self.rightAdd = self.error.returnRCorr() + self.lostLineBoost()
            self.leftAdd = -20 - self.error.returnRCorr() - self.lostLineBoost()
            self.lastTurn = 'r'

        def turnLeft(self):
            self.leftAdd = self.error.returnLCorr() + self.lostLineBoost()
            self.rightAdd = -20 - self.error.returnLCorr() - self.lostLineBoost()
            self.lastTurn = 'l' 

        def clearAdd(self):
            self.rightAdd = 0
            self.leftAdd = 0 

        def findLineLeft(self):
            self.turnLeft()
            self.drive()
            while(self.error.sense.leftReadout < self.error.sense.lNormalValue):
                #self.turnLeft()
                self.error.sense.readout()
                self.error.updateValues()
            self.clearAdd()
            self.drive()

        def findLineRight(self):
            self.turnRight()
            self.drive()
            while(self.error.sense.rightReadout < self.error.sense.rNormalValue):
                self.error.sense.readout()
                self.error.updateValues()
            self.clearAdd()
            self.drive()

        def setNormalSpeed(self, speed):
            self.normalSpeed = speed

        def checkLine(self):
            if self.error.sense.lostLine():
                self.setNormalSpeed(0)
            else:
                 self.setNormalSpeed(20)



    class gripper:
        def __init__(self):
            self.servo = MediumMotor(OUTPUT_B)
            self.isClosed = False
            self.closeAngle = 38
            
         
            
        def open(self):
            self.servo.on_for_degrees(SpeedPercent(20), self.closeAngle)
            self.isClosed = False

        def close(self):
            self.servo.on_for_degrees(SpeedPercent(20), self.closeAngle)
            self.isClosed = True

        def isClosed(self):
            return self.isClosed

    

    print('Inicjalizacja sensorow oraz silnikow')
    sense = Senses()
    errHandler  = ErrorHandler(sense)
    motors = Wheels(True, errHandler)
    gripper = gripper()

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
                #motors.turnLeft()
                motors.findLineLeft()
            elif sense.rightIsCrossing():
                print('Skrecam w prawo')
                motors.checkLine()
                #motors.turnRight()
                motors.findLineRight()
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
            
            
        
