import math
import random

def func1():
    print "hello"
func1()

def func2(lists):
    j = 0
    for i in lists:
        j += i
    return j

myList = [1.0,5.0,6.0,7.0,5.0,1.0,1.0,1.0,4.0]
a = func2(myList)
print a

def func3(lists):
    j = 0
    for i in lists:
        j += i
    return j/len(lists)

a = func3(myList)
print a

def func4(lists):
    return max(lists)

a = func4(myList)
print a
def func5(lists):
    return min(lists)

a = func5(myList)
print a

def func6(lists):
    return max(lists) - min(lists)

a = func6(myList)
print a
print " "
def func7(lists):
    u=[]
    for i in lists:
        seen = False
        for j in u:
            if i == j:
                seen = True
        if not seen:
            u.append(i)
    return u

a = func7(myList)
print a

def func8(a):
    u = []
    for i in a:
        seen = False
        for j in u:
            if i == j:
                seen = True
        if not seen:
            u.append(i)
    return u

print func8("Strooong")

def alphabetical(string):
    u = func8(string)
    j = u[0]

    for i in u:
        if j <= i:
            j = i

    return j

print alphabetical("allz")
print alphabetical("zlla")



number = random.randint(0, 100)
won = False

for i in range(1,5):
    guess = int(input("Guess a number"))
    if guess < number:
        print("My number is bigger")
    elif guess > number:
        print("My number is smaller")
    else:
        print("You guessed it!")
        won = True
