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


# Class defining x, y and z vectors and the vector arrow-head appearance/size.
# Inputs are an x, y and z vector (two points in a list for each axes)
# the scale of the arrow (mutation_scale), the thickness of the arrow (lw), the
# type of arrowhead (arrowstyle) and the arrow colour (color).
# Outputs a 3D vector with an arrowhead pointing in the direction of the given
# vector.
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)


# Function converting GPS coordinates into ECI (Earth-Centred Interial)
# coordinates.
# Inputs are Latitude, Longitude and Elevation.
# Outputs a list containing the x, y and z coordinates of the given GPS input
# with respect to the centre of the Earth.
def ECI_Conversion(lat, lon, el):
    now = datetime.datetime.utcnow()
    STt0 = SidTime(JulianDay(now.year, now.month, now.day), lon, now.hour,
                   now.minute, now.second)
    return Geocentric(lat, STt0, el)


#####################################################

# Read data from radar, vector to target, distance and elevation
# Convert data if necessary to find location of target in ECI coordinates
# Code here will replace code below

#####################################################

# Reads the number of lines(data points) in the file, necessary for the number
# of loops required in the final part of the program
with open('ISSGPS.txt') as f:
    data_points = sum(1 for line in f)

# Reading longitude and latitude from csv file and storing them in lists
Lat = []
Long = []

with open('ISSGPS.txt', 'r') as csvfile:
    coords = csv.reader(csvfile, delimiter=',')
    for row in coords:
        Lat.append(float(row[0]))
        Long.append(float(row[1]))

# Given in kilometres
Elev = 402.450

GS0 = ECI_Conversion(Lat[0], Long[0], Elev)

xd = GS0[0]
yd = GS0[1]
zd = GS0[2]

Target = np.array([xd, yd, zd])

######################################################

# Reads latitude and longitude of the ground station from a GPS device. The
# loop runs through the different USB ports to find the one that the GPS device
# is connected to

# Code needs to be changed in order to detect the name of the GPS device and
# ensure that the program selects the correct USB port when running
n = 0
for m in range(0,2):
        port = '/dev/ttyUSB' + str(i)
        ser = serial.Serial(port, 4800, timeout = 5)

        while True:
            line = ser.readline()
            splitline = line.split(",")

            if splitline[0] == '$GPGGA':
                latitude = splitline[2]
                latDirec = splitline[3]
                longitude = splitline[4]
                longDirec = splitline[5]
                break
        if latitude == '' or longitude == '':
            n += 1
        else:
            break

# Exits program if GPS device is not reading data/connecting to GPS satellites
# otherwise converts the given latitude and longitude into the required form.
# Inputs are the latitude and longitude deteced by the GPS device
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

# Retrieves the elevation of GPS location from geocoder module in metres and
# converts it into kilometres. Inputs are the latitude and longitude of the
# ground station
g = geocoder.elevation([Ground_Lat, Ground_Long])
Ground_Elev = float(g.meters/1000.0)
print 'Ground Elevation: ' + str(Ground_Elev)

##################################################

# Convert from ECI to Azimuth-Elevation coordinates using functions from the
# file Basis.py (JulianDay, SidTime, Topocentric and Angles)
# Inputs for JulianDay are the current time and output is the Julian Day.
# Inputs for SidTime are the Julian Day, the longitude of the ground
# station and the current international time (hour, minute, second). The output
# is sidereal time in degrees.
# Inputs for Topocentric are arrays containing the ECI coordinates of the
# ground station and the target, the ground station latitude and the sidereal
# time. Outputs the cartesian coordinates to the target in the topocentric
# frame centred on the ground station.
# Input for Angles is the Topocentric output and it returns the distance to
# the ground station, the elevation angle and azimuth angle needed to view the
# target.
GS1 = ECI_Conversion(Ground_Lat, Ground_Long, Ground_Elev)

xo = GS1[0]
yo = GS1[1]
zo = GS1[2]

Ground = np.array([xo, yo, zo])

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Ground_Long, now.hour,
               now.minute, now.second)

Top = Topocentric(Ground, Target, Ground_Lat, STt0)

AzEl = Angles(Top)

fd = open('AziEle.csv','a')
fd.write(str(AzEl[0]))
fd.write(',')
fd.write(str(AzEl[1]))
fd.write(',')
fd.write(str(AzEl[2]))
fd.write('\n')
fd.close()

#####################################################

# Defines figure as 3D and then as interactive using matplotlib (vectors can be
# added and removed)
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

# Definition of the x, y and z vectors from the station to the target
x = [xo, xd]
y = [yo, yd]
z = [zo, zd]

# Defines and adds vector to figure using the Arrow3D class. Inputs are the x,
# y and z vectors, the scale of the vector, the size of the arrowhead, the
# arrow style and the colour of the vector
a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="r")

ax.add_artist(a)


# Condition for the target being below the horizon. -5 degrees was chosen
# arbitrarily, this condition will change depending on the ground station
# location. Code should be added to the preference required.
if AzEl[1] < -5.0:
    print "Target is currently below the horizon."


# Loop updating the vector from the ground station to the target for the number
# of data points in the file. The loop contains an if statement to check if
# the target is below the horizon and stops tracking it on the figure if it is.
i = 1

while True:
    a.remove()

    GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
    xd = GS0[0]
    yd = GS0[1]
    zd = GS0[2]
    Target = np.array([xd, yd, zd])

    Top = Topocentric(Ground, Target, Ground_Lat, STt0)
    AzEl = Angles(Top)

    fd = open('AziEle.csv','a')
    fd.write(str(AzEl[0]))
    fd.write(',')
    fd.write(str(AzEl[1]))
    fd.write(',')
    fd.write(str(AzEl[2]))
    fd.write('\n')
    fd.close()

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

        # Loop updating position of target and checking if it is above the
        # ground station's horizon (-5 degrees was chosen arbitrarily). The
        # position vector is plotted if it is above the horizon.
        while True:
            if AzEl[1] < -5.0:
                GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
                xd = GS0[0]
                yd = GS0[1]
                zd = GS0[2]
                Target = np.array([xd, yd, zd])

                Top = Topocentric(Ground, Target, Ground_Lat, STt0)
                AzEl = Angles(Top)

                fd = open('AziEle.csv','a')
                fd.write(str(AzEl[0]))
                fd.write(',')
                fd.write(str(AzEl[1]))
                fd.write(',')
                fd.write(str(AzEl[2]))
                fd.write('\n')
                fd.close()

                plt.pause(0.05)

                if i < data_points - 1:
                    i += 1

            else:
                GS0 = ECI_Conversion(Lat[0 + i], Long[0 + i], Elev)
                xd = GS0[0]
                yd = GS0[1]
                zd = GS0[2]
                Target = np.array([xd, yd, zd])

                Top = Topocentric(Ground, Target, Ground_Lat, STt0)
                AzEl = Angles(Top)

                fd = open('AziEle.csv','a')
                fd.write(str(AzEl[0]))
                fd.write(',')
                fd.write(str(AzEl[1]))
                fd.write(',')
                fd.write(str(AzEl[2]))
                fd.write('\n')
                fd.close()

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

# Loop keeps the interactive figure open indefinitely
while True:
    plt.pause(0.05)
