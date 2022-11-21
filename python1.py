#!/usr/bin/env python3
from time import sleep

from ev3dev2.led import Leds
from ev3dev2.motor import (OUTPUT_A, OUTPUT_B, OUTPUT_C, LargeMotor,
                           MediumMotor,  SpeedPercent)
from ev3dev2.sensor import INPUT_3, INPUT_4, INPUT_2
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor

# TODO: Add code here


try:
    ENDFLAG = False
    NO_COLOR = 0
    BLACK = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5
    WHITE = 6
    BROWN = 7
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
            self.colorValue[NO_COLOR] = 0
            self.colorValue[BLACK] = 0
            self.colorValue[BLUE] = 0
            self.colorValue[GREEN] = 0
            self.colorValue[YELLOW] = 0
            self.colorValue[RED] = 0
            self.colorValue[WHITE] = 0

        def incBuffer(self, color):
            self.colorValue[color] += 1

        def clearBuffer(self):
            for i in range(len(self.colorValue)):
                self.colorValue[i] = 0


    
            

    class Senses:
        def __init__(self):
            self.leftSensor = ColorSensor(INPUT_3)
            self.rightSensor = ColorSensor(INPUT_4)
            #self.infraredSensor = InfraredSensor(INPUT_2)
            #self.infraredSensor.MODE_IR_PROX = 'IR-PROX'
            self.rightReadout = 0
            self.leftReadout = 0
            self.lastRightReadout = 0
            self.lastLeftReadout = 0
            self.alertValue = 28
            self.lNormalValue = 12
            self.rNormalValue = 10
            self.errorTrigger = 15
            self.leftAlert = 25
            self.rightAlert = 15
            self.hasLostLine = False
            self.lColorBuffer = color_buffer()
            self.rColorBuffer = color_buffer()

            # self.distanceToObject = 100

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

        '''
        def readDistance(self):
            temp = self.infraredSensor.proximity
            self.distanceToObject = self.infraredSensor.proximity
            return temp
        '''
        
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
            if self.rVal() > 25 and self.lVal() > 35:
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
            if (colors == (BLACK, BLACK) or colors == (WHITE, WHITE) or 
                colors == (BLACK, WHITE) or colors == (WHITE, BLACK)):
                #zaden kolor nie zostal znaleziony
                return (-1, -1)
            else:
                #jesli zostal, zwroc krotke kolorow
                return colors

        def clearBuffers(self):
            self.lColorBuffer.clearBuffer()
            self.rColorBuffer.clearBuffer()

        def compareReflectedLight(self):
            self.readout()
            leftOffset = 2
            print(self.leftReadout, self.rightReadout)
            if self.leftReadout - leftOffset < self.rightReadout:
                return 'l'
            elif self.leftReadout - leftOffset > self.rightReadout:
                return 'r'
            else:
                return 0

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
            self.proportional = 0.3
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

            #ErrorHandler
            self.error = errorHandler

            #Wartosci dodawane do silnika
            self.rightAdd = 0
            self.leftAdd = 0
            self.maxTurnAdd = 10 #maksymalna wartosc
            
            self.lastTurn = '0'

            self.normalSpeed = 10
            self.prepFractionSpeed = 10
            self.approachSpeed = 12
            self.overloadedSpeed = 25
            self.decreaseBoost = False

            self.speed = self.normalSpeed #Unused for now



        def setWheels(self, speedLeft, speedRight):
            #check wartosci, czy nie przekroczono wartosci maksymalnych
            if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
                print("Zla wartosc na silniku.")
                print(speedLeft, speedRight)
                return

            #odpalenie silnikow
            print(speedLeft, speedRight)
            self.leftMotor.on(SpeedPercent(speedLeft))
            self.rightMotor.on(SpeedPercent(speedRight))


        def setWheelsForTime(self, speedLeft, speedRight, time):
            if speedLeft>100 or speedRight>100 or speedLeft<-100 or speedRight<-100:
                print("Zla wartosc na silniku.")
                print(speedLeft, speedRight)
                return

            #odpalenie silnikow
            print('lewy')
            self.leftMotor.on_for_seconds(SpeedPercent(speedLeft), time)
            print('prawy')
            self.rightMotor.on_for_seconds(SpeedPercent(speedRight), time)


        def setWheelsForRotations(self, speedLeft, speedRight, lRot, pRot):
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
            if self.error.sense.hasLostLine == True and self.decreaseBoost == False:
                return 10
            elif self.error.sense.hasLostLine == True and self.decreaseBoost == True:
                return 3
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
        
        def stopWheels(self):
            self.rightMotor.stop()
            self.leftMotor.stop()

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

        def leftTurnPrep(self, time):
            self.stopWheels()
            self.leftMotor.on_for_rotations(SpeedPercent(self.prepFractionSpeed*1.5), 3)
            self.lastTurn = 'l' 

        def rightTurnPrep(self, time):
            self.stopWheels()
            self.rightMotor.on_for_rotations(SpeedPercent(self.prepFractionSpeed*2), time)
            self.lastTurn = 'r' 



        def leftWithdrawPrep(self, rots):
            self.stopWheels()
            self.leftMotor.on_for_rotations(SpeedPercent(-self.prepFractionSpeed*3), rots)

        def rightWithdrawPrep(self, rots):
            self.stopWheels()
            self.rightMotor.on_for_rotations(SpeedPercent(-self.prepFractionSpeed*3), rots)

        def straightWithdrawPrep(self, rots):
            self.stopWheels()
            self.leftAdd = -45
            self.rightAdd = -45
            self.drive()
            sleep(rots)
            self.clearAdd()
            self.stopWheels()
                


        def straightApproachPrep(self, rots):
            self.stopWheels()
            self.leftAdd = 5
            self.rightAdd = 5
            self.drive()
            sleep(rots)
            self.stopWheels()	    
         
        def leftRotationPrep(self, time):
            self.stopWheels()
            self.clearAdd()
            factor = 10
            self.rightAdd = -factor
            self.leftAdd = factor
            self.drive()
            sleep(time)
            self.stopWheels()
            self.clearAdd()       
        
        def rightRotationPrep(self, time):
            self.stopWheels()
            self.closeAdd()
            factor = 10
            self.rightAdd = factor
            self.leftAdd = -factor
            self.drive()
            sleep(time)
            self.stopWheels()
            self.clearAdd()


        def setSpeed(self, speed):
            self.Speed = speed

        def checkLine(self):
            #Niescislosc - w turnRight/Left jest juz wyzerowanie tej wartosci odjeciem -20
            #Teraz to sie powtarza i cos tu nie gra
            if self.error.sense.lostLine():
                self.setSpeed(0)
            else:
                 self.setSpeed(self.normalSpeed)
            



    class gripper:
        def __init__(self):
            self.servo = MediumMotor(OUTPUT_B)
            self.isClosed = False
            self.closeAngle = 45
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
            self.grabColors = [GREEN]
            self.placeColors = [GREEN]
            self.pickColors = [GREEN]
            self.unpickColors = [GREEN]
            self.grabbingProc = False
            self.placingProc = False
            self.colorsTuple = None
            self.colorDetectionCount = 2 #Ile razy w iteracji czujnik musi wykryc kolor zeby go zaakceptowac
            self.hasPickedObject = False


        
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
                    print('Linia zgubiona 1')
                    if self.motors.lastTurn == 'r':
                        self.motors.turnRight()
                    elif self.motors.lastTurn == 'l':
                        self.motors.turnLeft()
                    else:
                        pass

            elif(self.motors.error.sense.lostLine()):
                print("Linia Zgubiona")
                if self.motors.lastTurn =='r':
                    #self.motors.findLineRight()
                    self.motors.turnRight()
                elif self.motors.lastTurn == 'l':
                    #self.motors.findLineLeft()
                    self.motors.turnLeft()
            else:
                self.motors.clearAdd()
                print('Prosto')
        
            self.motors.drive()


        def gripperHandling(self):
            if(self.gripper.grabObj == True):
                self.gripper.close()
                self.gripper.grabObj = False
            elif(self.gripper.isClosed and self.gripper.grabObj == False):
                self.gripper.open()


        def checkForColoredLine(self):
            if ENDFLAG==True:
                return
            temp = self.motors.error.sense.checkColor()
            if temp == (-1, -1):
                self.motors.error.sense.clearBuffers()
                return (-1, -1)
            else:
                if self.hasPickedObject == False:
                    if temp[0] in self.grabColors : # Czy kolor znajduje sie w zbiorze pozadanych kolorow?
                        if self.motors.error.sense.lColorBuffer.colorValue[temp[0]] >= self.colorDetectionCount: # Czy przekroczyl on minimalna ilosc iteracji
                            self.grabbingProc = True    # jesli tak, to zalacz procedure odbioru/przekazania klocka
                            self.colorsTuple = (temp[0], 0)
                            self.motors.error.sense.clearBuffers()
                            return temp[0]
                    elif temp[1] in self.grabColors:
                        if self.motors.error.sense.rColorBuffer.colorValue[temp[1]] >= self.colorDetectionCount:
                            self.grabbingProc = True
                            self.colorsTuple = (0, temp[1])
                            self.motors.error.sense.clearBuffers()
                            return temp[1]
                    else:
                        self.motors.error.sense.clearBuffers()
                else:
                    if temp[0] in self.placeColors:
                        if self.motors.error.sense.lColorBuffer.colorValue[temp[0]] >= self.colorDetectionCount:
                            self.placingProc = True
                            self.colorsTuple = (temp[0], 0)
                            self.motors.error.sense.clearBuffers()
                            return temp[0]
                    elif temp[1] in self.placeColors:
                        if self.motors.error.sense.rColorBuffer.colorValue[temp[1]]  >= self.colorDetectionCount:
                            self.placingProc = True
                            self.colorsTuple = (0, temp[1])
                            self.motors.error.sense.clearBuffers()
                            return temp[0]
                    else:
                        self.motors.error.sense.clearBuffers()

        def checkForColor(self):
            temp = self.motors.error.sense.checkColor()
            if temp == (-1, -1):
                self.motors.error.sense.clearBuffers()
                return (-1, -1)
            elif self.hasPickedObject == False:
                if temp[0] in self.pickColors or temp[1] in self.pickColors:
                    if self.motors.error.sense.rColorBuffer.colorValue[temp[1]] >= self.colorDetectionCount and temp[1] in self.pickColors:
                        self.motors.error.sense.clearBuffers()
                        return temp[0]
                    if self.motors.error.sense.lColorBuffer.colorValue[temp[0]] >= self.colorDetectionCount and temp[0] in self.pickColors:
                        self.motors.error.sense.clearBuffers()
                        return temp[1]
                elif temp[0] not in self.pickColors and temp[1] not in self.pickColors:
                    #to nie ten kolor
                    self.motors.error.sense.clearBuffers()
                    return (-2, -2)
                else:
                    self.motors.error.sense.clearBuffers()
            elif self.hasPickedObject == True:
                if temp[0] in self.unpickColors or temp[1] in self.unpickColors:
                    if self.motors.error.sense.rColorBuffer.colorValue[temp[1]] >= self.colorDetectionCount and temp[1] in self.unpickColors:
                        self.motors.error.sense.clearBuffers()
                        return temp[0]
                    if self.motors.error.sense.lColorBuffer.colorValue[temp[0]] >= self.colorDetectionCount and temp[0] in self.unpickColors:
                        self.motors.error.sense.clearBuffers()
                        return temp[1]
                elif temp[0] not in self.unpickColors and temp[1] not in self.unpickColors:
                    self.motors.error.sense.clearBuffers()
                    return (-2, -2)
                else:
                    self.motors.error.sense.clearBuffers()

        def grabbingProcedure(self, searchedColor):
            if self.grabbingProc == False:
                return
            elif ENDFLAG == True:
                return
            else:
                self.motors.stopWheels()
                if(self.colorsTuple[0] != 0 or self.colorsTuple[1] != 0):
                    direction = self.motors.error.sense.compareReflectedLight()
                    if direction == 'l':
                        #dojscie
                        print("Podniesienie z lewej")
                        self.motors.decreaseBoost = True
                        self.motors.stopWheels()
                        sleep(2)
                        self.motors.straightApproachPrep(1)
                        self.motors.leftRotationPrep(2)
                        #Szukaj linii
                        self.motors.turnLeft()
                        self.motors.drive()
                        while(self.motors.error.sense.lostLine()):
                                self.motors.error.sense.readout()
                                self.motors.error.updateValues()
                        print('Szukam koloru za kolorem')
                        self.motors.stopWheels()
			            #Jadac po linii, szukaj koloru
                        givenColor = self.checkForColor()
                        while(givenColor != searchedColor):
                            for i in range(3):
                                self.followLine()
                            givenColor = self.checkForColor()
                            print(givenColor)
                        print('Kolor znaleziony')
                        self.motors.stopWheels()
                        #Jesli to ten kolor, podjedz pod niego i go zlap
                        if(givenColor == searchedColor):
                            self.gripperHandling()
                            self.hasPickedObject = True
                            self.grabbingProc = False
                        else:
                            pass
                        #odejscie
                        self.grabbingProc = False
                        self.motors.straightWithdrawPrep(2)
                        self.motors.rightTurnPrep(1)
                        self.motors.lastTurn = 'l'
                        
                        
                    elif direction == 'r':
                        #dojscie
                        pass
                        


        def placingProcedure(self, searchedColor):
            if(self.placingProc == False):
                return
            else:
                self.motors.stopWheels()
                if(self.colorsTuple[0] != 0 or self.colorsTuple[1] != 0):
                    direction = self.motors.error.sense.compareReflectedLight()
                    if direction == 'l':
                        #dojscie
                        print("Podniesienie z lewej")
                        self.motors.decreaseBoost = True
                        self.motors.stopWheels()
                        sleep(2)
                        self.motors.straightApproachPrep(1)
                        self.motors.leftTurnPrep(1)
                        #Szukaj linii
                        while(self.motors.error.sense.lostLine()):
                                self.motors.error.sense.readout()
                                self.motors.error.updateValues()
                                self.motors.turnRight()
                                self.motors.drive()
                        givenColor = self.checkForColor()
                        while givenColor != searchedColor:
                            self.followLine()
                            givenColor = self.checkForColor()
                        self.motors.stopWheels()
                        if(givenColor == searchedColor):
                            self.gripperHandling()
                            self.hasPickedObject = False
                            ENDFLAG = True
                        #odejscie
                        self.grabbingProc = False
                        self.motors.straightWithdrawPrep(2)
                        self.motors.rightTurnPrep(1)
                        self.placingProc = False
                        self.motors.lastTurn = 'l'
                

    print('Inicjalizacja...')
    sense = Senses()
    errHandler  = ErrorHandler(sense)
    motors = Wheels(True, errHandler)
    gripper = gripper()
    robot = robot(motors, gripper)

    print('Entering the loop...')
    #Glowna petla
    while(ENDFLAG == False):
        for i in range(2):
            robot.followLine()
        robot.checkForColoredLine()
        robot.grabbingProcedure(robot.pickColors[0])
        robot.placingProcedure(robot.placeColors[0])
        
        print(sense.leftReadout, sense.rightReadout)
        #TESTY
        #robot.followLine()

        #robot.motors.error.sense.checkColor()
        
        #robot.checkForColor()
        
        
except KeyboardInterrupt: #ctrl+c
    try:
        motors.setWheels(0,0)
    except:
        pass

    print("Program zakonczony przez uzytkownika")
            
            
        
