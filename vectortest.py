import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import random
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

# Station coordinates in km
xo = 1700.93858271
yo = 3580.30200345
zo = 2099.78692214

Elev = 1503.0
Re = 6378.0

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Long[0], now.hour, now.minute, now.second)
GS0 = Geocentric(Lat[0], STt0, Elev)

xd = GS0[0]
yd = GS0[1]
zd = GS0[2]


# MOVING STATION GPS TO CARTESIAN

# Radius of Earth
#Re = 6378.0
# Actual sidereal time
#now = datetime.datetime.utcnow()
#STt0 = SidTime(JulianDay(now.year, now.month, now.day), Long, now.hour, now.minute, now.second)
#GS0 = [x0, y0, z0] contain the coordinates of Ground Station with geocentric reference
#GS0 = Geocentric(lat, STt0, Elev)

#xo = GS0[0]
#yo = GSO[1]
#zo = GSO[2]


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


def timer():
    return time.time() - to


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



traj = Trajectory(math.cos(timer()), math.cos(timer()), 0.0)
Ax = traj.get_xaccel()
Ay = traj.get_yaccel()
Az = traj.get_zaccel()
Vx = traj.get_xvel(50.0)
Vy = traj.get_yvel(50.0)
Vz = traj.get_zvel(0.0)


# Defines figure as 3D
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

x = [xo, xd]
y = [yo, yd]
z = [zo, zd]

a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="k")
# Draw line on plot
ax.add_artist(a)

# Loop updating vector from station to target
while True:

    a.remove()
    xd = xd + 0.5*Ax*timer()**2 + Vx*timer()
    yd = yd + 0.5*Ay*timer()**2 + Vy*timer()
    zd = zd + 0.5*Az*timer()**2 + Vz*timer()

    x = [xo, xd]
    y = [yo, yd]
    z = [zo, zd]

    a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
                color="k")
    ax.add_artist(a)

    plt.pause(0.05)


# Keeps figure open
while True:
    plt.pause(0.05)
