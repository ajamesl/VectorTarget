import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import csv
import datetime
import math
from Basis import *


Long = []
Lat = []

# Reading longitude and latitude from file
with open('radar.txt', 'r') as csvfile:
    coords = csv.reader(csvfile, delimiter=',')
    for row in coords:
        Long.append(float(row[0]))
        Lat.append(float(row[1]))

# Radius of Earth
Re = 6378.135

# Ground station location GPS coords. to Topocentric

# Read longitude and latitude from GPS #
########################################
Ground_Long = [-40]
Ground_Lat = [20]
########################################

now = datetime.datetime.utcnow()
STt0 = SidTime(JulianDay(now.year, now.month, now.day), Ground_Long[0],
               now.hour, now.minute, now.second)

# GPS to ECI conversion
omega = (2*math.pi)/86164.0916
du = JulianDay(now.year, now.month, now.day) - 2451545.0
Tu = du/36525.0
theta0 = ( 24110.54841 + (8640184.812866 * Tu) + (0.093104 * Tu**2)
           - (0.0000062 * Tu**3) )

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
Ground = np.array([xo, yo, zo])

# Drone ECI
R_d = Re * math.cos(Lat[0])
phi_d = Lat[0]
theta_d = degangle + Long[0]
if theta_d > 360:
    theta_d = theta_d - 360.0

xd = R_d * math.cos(theta_d)
yd = R_d * math.sin(theta_d)
zd = Re * math.sin(phi_d)
Drone = np.array([xd, yd, zd])


# ECI to Topocentric (Azimuth/Elevation) conversio

rx = xd - xo
ry = yd - yo
rz = zd - zo

rS = ( math.sin(phi)*math.cos(theta)*rx + math.sin(phi)*math.sin(theta)*ry
       - math.cos(phi)*rz )
rE = -math.sin(theta)*rx + math.cos(theta)*ry
rZ = ( math.cos(phi)*math.cos(theta)*rx + math.cos(phi)*math.sin(theta)*ry
       + math.sin(phi)*rz )

r = math.sqrt(rS**2 + rE**2 + rZ**2)
Rt = np.array([rS, rE, rZ])

if Rt[0] != 0 or Rt[1] != 0 or Rt[2] != 0:
    RTop = (1/r)*Rt

    El = math.asin(-rZ/r)*(180.0/math.pi)
    # Protection cases, angles near to pi/2
    if (abs(El - 90.0) < 0.01):
        # No azimuth angle
        Az = 0.0
    else:
        # To calculate the quadrant of angle, we need the signs of cosAz and
        # sinAz
        sinAz = (RTop[0])/math.cos(El*math.pi/180.0)
        cosAz = (RTop[1])/math.cos(El*math.pi/180.0)

        # First value, but without quadrant
        Az = math.atan(rE/rS)*(180.0/math.pi)

        # Check the quadrant
        # First quadrant
        if ((sinAz >= 0) and (cosAz >= 0)):
            Az = Az

        # Second quadrant
        elif ((sinAz >= 0) and (cosAz <= 0)):
            Az = Az

        # Third quadrant
        elif ((sinAz <= 0) and (cosAz <= 0)):
            Az = 360.0 - Az

        # Fourth quadrant
        else:
            Az = 360.0 - Az
else:
    El = 90.0
    Az = 0.0

print "Elevation: " + str(El)
print "Azimuth: " + str(Az)
print "Distance: " + str(r)


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


# Defines figure as 3D and interactive
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Axes ranges & labels
ax.set_xlim([-10000, 10000])
ax.set_ylim([-10000, 10000])
ax.set_zlim([0, 10000])
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Conversion from Elevation, Azimuth & Distance to Cartesian
X = r*math.sin(El)*math.cos(Az)
Y = r*math.sin(El)*math.sin(Az)
Z = r*math.cos(El)

# Definition of the vector from the station to the target
x = [0, X]
y = [0, Y]
z = [0, Z]

# Define and draw vector on figure
a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="k")
ax.add_artist(a)

plt.show()
