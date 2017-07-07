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


def ECI_Conversion(lat, lon, el):
    now = datetime.datetime.utcnow()
    STt0 = SidTime(JulianDay(now.year, now.month, now.day), lon, now.hour,
                   now.minute, now.second)
    return Geocentric(lat, STt0, el)


to = time.time()

# Reading longitude and latitude from file
Lat = []
Long = []

with open('ISSGPS.txt', 'r') as csvfile:
    coords = csv.reader(csvfile, delimiter=',')
    for row in coords:
        Lat.append(float(row[0]))
        Long.append(float(row[1]))

# In km
Elev = 402.450

GS0 = ECI_Conversion(Lat[0], Long[0], Elev)

xd = GS0[0]
yd = GS0[1]
zd = GS0[2]


# MOVING STATION GPS TO CARTESIAN

# Read latitude and longitude from GPS #
########################################
# Medellin GPS location
Ground_Lat = [6.253362]
Ground_Long = [-75.574419]
########################################


# Read Elevation (km) of Ground Station from Google API
##################################################
Ground_Elev = 1.503
##################################################


GS1 = ECI_Conversion(Ground_Lat[0], Ground_Long[0], Ground_Elev)

xo = GS1[0]
yo = GS1[1]
zo = GS1[2]


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


# Defines figure as 3D and interactive
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

plt.ion()

u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 18)

xs = 6378.135 * np.outer(np.cos(u), np.sin(v))
ys = 6378.135 * np.outer(np.sin(u), np.sin(v))
zs = 6378.135 * np.outer(np.ones(np.size(u)), np.cos(v))

c = ax.plot_surface(xs, ys, zs, rstride=1, cstride=1, color='w', shade=0)
ax.add_artist(c)

# Axes ranges & labels
ax.set_xlim([-7000, 7000])
ax.set_ylim([-7000, 7000])
ax.set_zlim([-7000, 7000])
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Definition of the vector from the station to the target
x = [xo, xd]
y = [yo, yd]
z = [zo, zd]

# Define and draw vector on figure
a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="r")
ax.add_artist(a)

t = 0
i = 1

# Loop updating vector from station to target
while True:

    a.remove()

    GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
    xd = GS0[0]
    yd = GS0[1]
    zd = GS0[2]

    x = [xo, xd]
    y = [yo, yd]
    z = [zo, zd]

    a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
                color="r")
    ax.add_artist(a)

    plt.pause(0.05)
    if i < 39:
        i += 1

# Keeps figure open
while True:
    plt.pause(0.05)
