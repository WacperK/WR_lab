#!/usr/bin/env python3
from time import sleep

from ev3dev2.led import Leds
from ev3dev2.motor import (OUTPUT_A, OUTPUT_B, OUTPUT_C, LargeMotor,
                           MediumMotor, ServoMotor, SpeedPercent)
from ev3dev2.sensor import INPUT_3, INPUT_4, INPUT_2
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor

# TODO: Add code here


try:
    class colors:
        def __init__(self):
            self.colorsCount = 8
            self.NO_COLOR = 0
            self.BLACK = 1
            self.BLUE = 2
            self.GREEN = 3
            self.YELLOW = 4
            self.RED = 5
            self.WHITE = 6
            self.BROWN = 7

        def valueToColor(self, value):
            if value == self.BLACK:
                return 'black'
            elif value == self.BLUE:
                return 'blue'
            elif value == self.GREEN:
                return 'green'
            elif value == self.YELLOW:
                return 'yellow'
            elif value == self.RED:
                return 'red'
            elif value == self.WHITE:
                return 'white'
            elif value == self.NO_COLOR:
                return 'no color'
            else:
                print('Value not attached to a specific color')
                return -1
            
    colors = colors()

    class color_buffer:
        def __init__(self):
            self.itemsNumber = 5
            self.colorValue = [0 for i in range(8)]
            self.colorValue[colors.NO_COLOR] = 0
            self.colorValue[colors.BLACK] = 0
            self.colorValue[colors.BLUE] = 0
            self.colorValue[colors.GREEN] = 0
            self.colorValue[colors.YELLOW] = 0
            self.colorValue[colors.RED] = 0
            self.colorValue[colors.WHITE] = 0

        def incBuffer(self, color):
            self.colorValue[color] += 1

        def clearBuffer(self):
            for i in range(len(self.colorValue)):
                self.colorValue[i] = 0


    
            

    class Senses:
        def __init__(self):
            self.leftSensor = ColorSensor(INPUT_3)
            self.rightSensor = ColorSensor(INPUT_4)
            self.infraredSensor = InfraredSensor(INPUT_2)
            self.infraredSensor.MODE_IR_PROX = 'IR-PROX'
            self.rightReadout = 0
            self.leftReadout = 0
            self.lastRightReadout = 0
            self.lastLeftReadout = 0
            self.alertValue = 28
            self.lNormalValue = 12
            self.rNormalValue = 10
            self.errorTrigger = 15
            self.leftAlert = 20
            self.rightAlert = 15
            self.hasLostLine = False
            self.lColorBuffer = color_buffer()
            self.rColorBuffer = color_buffer()

            self.distanceToObject = 100

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

        def readDistance(self):
            temp = self.infraredSensor.proximity
            self.distanceToObject = self.infraredSensor.proximity
            return temp

        def readRightColor(self):
            temp = self.rightSensor.color
            return temp

        def readLeftColor(self):
            temp = self.leftSensor.color
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
            #Uwaga = Tutaj wartosci pozostaly niezmienione
            if self.rVal() > 30 and self.lVal() > 35:
                self.hasLostLine = True
                return True
            else:
                self.hasLostLine = False
                return False

        def readColorProc(self):
            for i in range(self.lColorBuffer.itemsNumber):
                self.lColorBuffer.incBuffer(self.readLeftColor())
                self.rColorBuffer.incBuffer(self.readRightColor())

        def findBestColor(self):
            lValue = max(self.lColorBuffer.colorValue)
            rValue = max(self.rColorBuffer.colorValue)
            lColor = self.lColorBuffer.colorValue.index(lValue)
            rColor = self.rColorBuffer.colorValue.index(rValue)
            return (lColor, rColor)

        def checkColor(self):
            self.readColorProc()
            colors = self.findBestColor()
            if colors == (colors.BLACK, colors.BLACK) or colors == (colors.WHITE, colors.WHITE) or (colors.BLACK, colors.WHITE) or (colors.WHITE, colors.BLACK):
                return -1
            else:
                return colors

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
            self.normalSpeed = 18
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


        def setWheelsForTime(self, speedLeft, speedRight, time):
            if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
                print("Zla wartosc na silniku.")
                print(speedLeft, speedRight)
                return

            #odpalenie silnikow

            self.leftMotor.on_for_seconds(SpeedPercent(speedLeft), time)
            self.rightMotor.on_for_seconds(SpeedPercent(speedRight), time)


        def setWheelsForRotations(self, speedLeft, speedRight, lRot, pRot):
            if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
                print("Zla wartosc na silniku.")
                print(speedLeft, speedRight)
                return

            #odpalenie silnikow

            self.leftMotor.on_for_rotations(SpeedPercent(speedLeft), lRot)
            self.rightMotor.on_for_rotations(SpeedPercent(speedRight), pRot)

        
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

        def setSpeed(self, speed):
            self.Speed = speed

        def checkLine(self):
            if self.error.sense.lostLine():
                self.setSpeed(0)
            else:
                 self.setSpeed(self.normalSpeed)



    class gripper:
        def __init__(self):
            self.servo = MediumMotor(OUTPUT_B)
            self.isClosed = False
            self.closeAngle = 38
            self.grabObj = True
            
         
        #Zamykanie i otwieranie chwytaka ze sprawdzeniem, czy przypadkiem nie jest juz otwarty (pozycjonowanie w przyrostowym)    
        def open(self):
            if self.isClosed:
                self.servo.on_for_degrees(SpeedPercent(10), -self.closeAngle)
                self.isClosed = False
            else:
                pass

        def close(self):
            if self.isClosed == False:
                self.servo.on_for_degrees(SpeedPercent(10), self.closeAngle)
                self.isClosed = True
            else:
                pass

        def isClosed(self):
            return self.isClosed

        # Czy chwytak powinien zlapac objekt przy kontakcie
        def setGrab(self):
            self.grabObj = True

        def resetGrab(self):
            self.grabObj = False

    class robot:
        def __init__(self, motors, gripper):
            self.motors = motors
            self.gripper = gripper
            self.grabColors = [colors.RED]
            self.placeColors = [colors.BLUE]
            self.grabbingProc = False
            self.placingProc = False
            self.colorsTuple = None
            self.colorDetectionCount = 2 #Ile razy w iteracji czujnik musi wykryc kolor zeby go zaakceptowac

        
        def followLine(self):
            self.motors.error.sense.readout()
            self.motors.error.updateValues()
        
            if self.motors.error.sense.rightIsCrossing() or self.motors.error.sense.leftIsCrossing() or self.motors.error.sense.lostLine():
                if self.motors.error.sense.rightIsCrossing() and self.motors.error.sense.leftIsCrossing():
                    print('Skrzyzowanie')
                    self.motors.clearAdd()
                elif self.motors.error.sense.leftIsCrossing():
                    print('Skrecam w lewo')
                    self.motors.checkLine()
                    #motors.turnLeft()
                    self.motors.findLineLeft()
                elif self.motors.error.sense.rightIsCrossing():
                    print('Skrecam w prawo')
                    self.motors.checkLine()
                    #motors.turnRight()
                    self.motors.findLineRight()
                elif self.motors.error.sense.lostLine():
                    if self.motors.lastTurn == 'r':
                        self.motors.turnRight()
                    elif self.motors.lastTurn == 'l':
                        self.motors.turnLeft()
                    else:
                        pass

            elif(self.motors.error.sense.lostLine()):
                print("Linia Zgubiona")
                if self.motors.lastTurn =='r':
                    self.motors.turnRight()
                elif self.motors.lastTurn == 'l':
                    self.motors.turnLeft()
            else:
                self.motors.clearAdd()
                print('Prosto')
        
            self.motors.drive()


        def gripperHandling(self):
            if(self.motors.error.sense.readDistance < 5 and self.gripper.grabObj == True):
                self.gripper.close()
            if(self.gripper.isClosed() and self.gripper.grabObj == False):
                self.gripper.open()


        def checkForColoredLine(self):
            temp = self.motors.error.sense.checkColor()
            if temp == -1:
                pass
            else:
                if temp[0] in self.grabColors : # Czy kolor znajduje sie w zbiorze pozadanych kolorow?
                    if self.motors.error.sense.lColorBuffer[temp[0]] > self.colorDetectionCount: # Czy przekroczyl on minimalna ilosc iteracji
                        self.grabbingProc = True    # jesli tak, to zalacz procedure odbioru/przekazania klocka
                        self.colorsTuple = temp
                elif temp[1] in self.grabColors:
                    if self.motors.error.sense.rColorBuffer[temp[1]] > self.colorDetectionCount:
                        self.grabbingProc = True
                        self.colorsTuple = temp
                elif temp[0] in self.placeColors:
                    if self.motors.error.sense.lColorBuffer[temp[0]] > self.colorDetectionCount:
                        self.placingProc = True
                        self.colorsTuple = temp
                elif temp[1] in self.placeColors:
                    if self.motors.error.sense.rColorBuffer[temp[1]] > self.colorDetectionCount:
                        self.placingProc = True
                        self.colorsTuple = temp
                else:
                    pass



    print('Inicjalizacja...')
    sense = Senses()
    errHandler  = ErrorHandler(sense)
    motors = Wheels(True, errHandler)
    gripper = gripper()
    robot = robot(motors, gripper)

    print('Entering the loop...')
    #Glowna petla
    while(1):
        for i in range(3):
            robot.followLine()
        robot.checkForColoredLine()
        
        
except KeyboardInterrupt: #ctrl+c
    try:
        motors.setWheels(0,0)
    except:
        pass

    print("Program zakonczony przez uzytkownika")
            
            
        
