import math

c = "Come"
d = "home"
print c + " " + d

for i in range(10):
    print "Hello"

for i in range (10):
    print i

for i in range(1,11):
    print i

for i in range(1,21):
    print i**2

for i in range(1,100):
    if i**2 < 1000:
        print i**2

for i in range(1,200):
    if i%3.0 == 0 and i%5.0 == 0:
        print i

s = 0
for i in range(1,101):
    s = s + i
print s

z = 0
for i in range(1,101):
    z = z + i**2
print z

print s**2 - z

for i in range(0,101):
    if i%3.0 == 0 and i%5.0 == 0:
        print "fizzbuzz"

    elif i%3.0 == 0:
        print "fizz"
    elif i%5.0 == 0:
        print "buzz"
    else:
        print i

x = 113
z = 0
for i in range(2,x):
    if x%i == 0:
        z += 1

if z > 0:
    print str(x) + " is not a prime number."
else:
    print str(x) + " is a prime number."

primesFound = 0
number = 0
while primesFound < 100:
    prime = True
    for i in range(2, number):
        if number % i == 0:
            prime = False
            break

    if prime:
          print(number)
          primesFound += 1

    number += 1

n = 102
for i in range (1,n):
    l = 1
    for j in range(1,i):
        l*=j
print str(n - 2) + " factorial is equal to " + str(l)

e = 0.0
n = 102
for i in range (1,n):
    l = 1
    for j in range(1,i):
        l*=j
    e += 1/l

print "e is equal to " + str(e)
print "The error on e is equal to " + str(e - math.e)

s = 0.0
a = 100
for i in range(1,a):
    n = 2.0*i + 1.0
    s += 1.0/n
print s

s = 0.0
a = 1000
for i in range(0,a):
    s += ((-1.0)**i)/((2.0*i) + 1.0)
print "Pi is equal to " + str(s*4)
print "With an error of " + str(s*4 - math.pi)

g = 1.0
h = 1.0
m = 100

for i in range(1,m):
    j = g + h
    g = h
    h = j

n3 = j

g = 1.0
h = 1.0
m = 101

for i in range(1,m):
    j = g + h
    g = h
    h = j

n4 = j

print n4/n3
