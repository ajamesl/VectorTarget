import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
from Basis import *
import numpy as np
import time
import csv
import datetime
import math
import geocoder
import serial
import sys


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


def ECI_Conversion(lat, lon, el):
    now = datetime.datetime.utcnow()
    STt0 = SidTime(JulianDay(now.year, now.month, now.day), lon, now.hour,
                   now.minute, now.second)
    return Geocentric(lat, STt0, el)


# Reads the number of lines(data points) in the file
with open('ISSGPS.txt') as f:
    data_points = sum(1 for line in f)


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

Drone = np.array([xd, yd, zd])


# Read latitude and longitude from GPS
########################################
ser = serial.Serial('/dev/ttyUSB0', 4800, timeout = 5)

while True:
    line = ser.readline()
    splitline = line.split(",")

    if splitline[0] == '$GPGGA':
        latitude = splitline[2]
        latDirec = splitline[3]
        longitude = splitline[4]
        longDirec = splitline[5]
        print line
        break

if latitude == '' or longitude == '':
    print "GPS device is not reading the ground station's location."
    sys.exit()

else:
    if latDirec == 'N':
        Ground_Lat = float(latitude)/100.0
    else:
        Ground_Lat = -float(latitude)/100.0

    if longDirec == 'E':
        Ground_Long = float(longitude)/100.0
    else:
        Ground_Long = -float(longitude)/100.0

# Get elevation from geocoder
g = geocoder.elevation([Ground_Lat, Ground_Long])
Ground_Elev = float(g.meters/1000.0)
print 'Elevation: ' + str(Ground_Elev)

##################################################

# Conver from ECI to Az-El coordinates
GS1 = ECI_Conversion(Ground_Lat, Ground_Long, Ground_Elev)

xo = GS1[0]
yo = GS1[1]
zo = GS1[2]

Ground = np.array([xo, yo, zo])

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Ground_Long, now.hour,
               now.minute, now.second)

Top = Topocentric(Ground, Drone, Ground_Lat, STt0)

AzEl = Angles(Top)


#####################################################

# Defines figure as 3D and interactive
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

plt.ion()


# Defines a sphere mesh to model the Earth with radius Re
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 18)

xs = 6378.135 * np.outer(np.cos(u), np.sin(v))
ys = 6378.135 * np.outer(np.sin(u), np.sin(v))
zs = 6378.135 * np.outer(np.ones(np.size(u)), np.cos(v))

c = ax.plot_surface(xs, ys, zs, rstride=1, cstride=1, color='w', shade=0)
ax.add_artist(c)


# Axes ranges & labels
ax.set_xlim([-6500, 6500])
ax.set_ylim([-6500, 6500])
ax.set_zlim([-6500, 6500])
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

if AzEl[1] < -5.0:
    print "Target is currently below the horizon."

i = 1

# Loop updating vector from station to target
while True:
    a.remove()

    GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
    xd = GS0[0]
    yd = GS0[1]
    zd = GS0[2]
    Drone = np.array([xd, yd, zd])

    Top = Topocentric(Ground, Drone, Ground_Lat, STt0)
    AzEl = Angles(Top)

    x = [xo, xd]
    y = [yo, yd]
    z = [zo, zd]

    a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
                color="r")
    ax.add_artist(a)

    plt.pause(0.05)

    if i < data_points - 1:
        i += 1

    if AzEl[1] < -5.0:
        print "Target is below the horizon."
        a.remove()

        # Loop updating position of target to check if it is above the
        # ground station's horizon
        while True:
            if AzEl[1] < -5.0:
                GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
                xd = GS0[0]
                yd = GS0[1]
                zd = GS0[2]
                Drone = np.array([xd, yd, zd])

                Top = Topocentric(Ground, Drone, Ground_Lat, STt0)
                AzEl = Angles(Top)

                plt.pause(0.05)

                if i < data_points - 1:
                    i += 1
            else:
                GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
                xd = GS0[0]
                yd = GS0[1]
                zd = GS0[2]
                Drone = np.array([xd, yd, zd])

                Top = Topocentric(Ground, Drone, Ground_Lat, STt0)
                AzEl = Angles(Top)

                x = [xo, xd]
                y = [yo, yd]
                z = [zo, zd]

                a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
                            color="r")
                ax.add_artist(a)

                plt.pause(0.05)

                if i < data_points - 1:
                    i += 1
                a.remove()


# Keeps figure open
while True:
    plt.pause(0.05)
