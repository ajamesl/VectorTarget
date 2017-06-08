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

print u[random.randint(0,5)]

print " "
print " "

class GuessingGame:
    def __init__(self):
        self.number = random.randint(1,101)
        win = False
        self.getGuess()

    def num(self):
        print self.number

    def getGuess(self):
        self.guess = int(input("Choose an integer between 1 and 100."))
        if self.guess < 1 or self.guess > 100:
            print "Invalid entry."
            self.getGuess()
        else:
            self.checkGuess()

    def checkGuess(self):
            if self.guess < self.number:
                print "Too low."
                self.getGuess()
            elif self.guess > self.number:
                print "Too high."
                self.getGuess()
            else:
                print "Well done. You guessed correctly."
                win = True

l = GuessingGame()
