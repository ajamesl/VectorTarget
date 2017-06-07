import math
import random

class PrintNumber:
    def __init__(self):
        self.numberToPrint = 3

    def wink(self):
        print(self.numberToPrint)

p = PrintNumber()
p.wink()

print math.sqrt(25)

print math.e**-1

print math.pi

print random.random()
print random.randint(0,100)

u = []
for i in range(0,6):
    u.append(random.random())

print u

print u[random.randint(0,6)]

print " "
print " "

class GuessingGame:
    def __init__(self):
        self.number = random.random()

    def num(self):
        print self.number

    def getGuess(self):
        

p = GuessingGame()
p.num()
