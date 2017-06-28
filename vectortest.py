import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import time
import csv
import datetime
import math
from Basis import *

to = time.time()

Long = []
Lat = []

# Reading longitude and latitude from file
with open('radar.txt', 'r') as csvfile:
    coords = csv.reader(csvfile, delimiter=',')
    for row in coords:
        Long.append(float(row[0]))
        Lat.append(float(row[1]))


Elev = 1503.0
Re = 6378.0

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Long[0], now.hour,
               now.minute, now.second)
GS0 = Geocentric(Lat[0], STt0, Elev)

xd = GS0[0]
yd = GS0[1]
zd = GS0[2]

# MOVING STATION GPS TO CARTESIAN

# Read longitude and latitude from GPS #
########################################
Ground_Long = [80]
Ground_Lat = [-30]
########################################

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Ground_Long[0],
               now.hour, now.minute, now.second)

# GPS to ECI conversion
omega = (2*math.pi)/86164.0916
du = JulianDay(now.year, now.month, now.day) - 2451545.0
Tu = du/36525.0
theta0 = 24110.54841 + (8640184.812866 * Tu) + (0.093104 * Tu**2) - (0.0000062 * Tu**3)

tau = datetime.datetime.utcnow()
deltatau = (tau.hour*60.0*60.0 + tau.minute*60.0 + tau.second)
thetatau = theta0 + omega * deltatau
secangle = thetatau - int(thetatau/86400.0)*86400.0
degangle = (secangle/86164.0916) * 360.0

# Ground station ECI
R = Re * math.cos(Ground_Lat[0])
phi = Ground_Lat[0]
theta = degangle + Ground_Long[0]
if theta > 360:
    theta = theta - 360.0

xo = R * math.cos(theta)
yo = R * math.sin(theta)
zo = Re * math.sin(phi)


# Class defining x, y, z vectors and the vector arrow-head appearance/size
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)


# Function defining time elapsed
def timer():
    return time.time() - to


# Class to find trajectory by inputting acceleration
class Trajectory():
    def __init__(self, ax, ay, az):
        self.__xaccel = ax
        self.__yaccel = ay
        self.__zaccel = az

    def get_xaccel(self):
        return self.__xaccel

    def get_yaccel(self):
        return self.__yaccel

    def get_zaccel(self):
        return self.__zaccel

    def get_xvel(self, vx0 = 0.0):
        return self.__xaccel*timer() + vx0

    def get_yvel(self, vy0 = 0.0):
        return self.__yaccel*timer() + vy0

    def get_zvel(self, vz0 = 0.0):
        return self.__zaccel*timer() + vz0


# Defining the trajectory of the target
traj = Trajectory(-5.0, 5.0, 0.0)
Ax = traj.get_xaccel()
Ay = traj.get_yaccel()
Az = traj.get_zaccel()
Vx = traj.get_xvel(0.0)
Vy = traj.get_yvel(0.0)
Vz = traj.get_zvel(0.0)

# Defines figure as 3D and interactive
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.ion()

# Axes ranges & labels
ax.set_xlim([-10000, 10000])
ax.set_ylim([-10000, 10000])
ax.set_zlim([-10000, 10000])
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Definition of the vector from the station to the target
x = [xo, xd]
y = [yo, yd]
z = [zo, zd]

# Define and draw vector on figure
a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="k")
ax.add_artist(a)

t = 0

# Loop updating vector from station to target
while True:

    a.remove()
    #xd = xd + 0.5*Ax*timer()**2 + Vx*timer()
    #yd = yd + 0.5*Ay*timer()**2 + Vy*timer()
    #zd = zd + 0.5*Az*timer()**2 + Vz*timer()
    xd = xd + 1000*math.cos(t)
    yd = yd + 1000*math.sin(t)
    zd = zd

    x = [xo, xd]
    y = [yo, yd]
    z = [zo, zd]

    a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
                color="k")
    ax.add_artist(a)

    plt.pause(0.05)
    t += (math.pi*1.0)/32.0

# Keeps figure open
while True:
    plt.pause(0.05)
