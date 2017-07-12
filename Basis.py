#!/usr/bin/env python2
# Functions to extract propesties of days and times

import datetime
import math
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

################################################################################
# Function to calculate the Julian Day based in Boulet (1991) and presented in the
# book "Orbital Mechanics for Engineering Students". The formulae works for years
# between 1901 < Y < 2099
def JulianDay(Y, M, D):
    JD = (367.0*Y) - math.trunc((7.0*(Y + math.trunc((M + 9.0)/12.0)))/4.0) + math.trunc(275.0*M/9.0) + D + 1721013.5
    # Return value
    return JD

################################################################################
# Function to calculate the Julian Day in all cases
def GeneralJulianDay(year, month, day):
    # Check values
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    # Check the beginning of the Gregorian calendar
    if((year < 1582) or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15)):
        # Before start of Gregorian calendar
        B = 0
    else:
        # After start of Gregorian calendar
        A = math.trunc(yearp / 100.0)
        B = 2 - A + math.trunc(A / 4.0)
    # Mean caculation
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
    D = math.trunc(30.601 * (monthp + 1))

    JD = B + C + D + day + 1720994.5
    # return Julian day
    return JD

################################################################################
# Funtion to calculate the sidereal time. The input is the Julian Day, the
# longitude of the place, and the international hour. Return the sidereal time
# in degrees
def SidTime(jd0, Long, H1, M1, S1):
    # Hours in UT1 format
    UTS1 = (H1) + (M1/60.0) + (S1/3600.0)
    # Sideral time in Greenwich to 0h
    T = (jd0 - 2451545.0)/(36525.0)
    Ts0 = (100.4606184) + (36000.77004*T) + (0.000387933*T*T) - ((T*T*T)/(38710000.0))
    # Between 0 and 360 degrees
    Ts0 = Ts0 - ((math.trunc(Ts0 / 360.0))*360.0)
    # Conversion to sexagesimal and add to hour and longitude
    TS = Ts0 + (360.98564724*(UTS1/24.0))
    TS = TS + Long
    if (TS >= 360.0):
        TS = TS - ((math.trunc(TS / 360.0))*360.0)
    elif (TS < 0):
        TS = TS + 360.0
    # return sideral time in degrees
    return TS

################################################################################
# Function to calculate the (x, y, z) position in geocentric form. For this the
# inputs are latitude, sideral time and elevation of the place
def Geocentric(Lat, SidTemp, H0):
    Pos = [0.0, 0.0, 0.0]
    Re = 6378.135
    f = 0.00335
    a = Re/(math.sqrt(1 - (((2*f) - (f*f))*((math.sin(Lat*math.pi/180.0))**2))))
    Pos[0] = (a + H0)*(math.cos(Lat*math.pi/180.0))*(math.cos(SidTemp*math.pi/180.0))
    Pos[1] = (a + H0)*(math.cos(Lat*math.pi/180.0))*(math.sin(SidTemp*math.pi/180.0))
    Pos[2] = ((a*(1 - f)*(1 - f)) + H0)*(math.sin(Lat*math.pi/180.0))
    # Return position in a list
    return Pos

################################################################################
# Function to calculate the elevation and azimuth angle for the topocentric frame
# The inputs are the coordinate of Ground station (RG) and satellites (RS),
# latitude (Lat) and sidereal time (ST0).
# The function return (distance to ground station (Dist), elevation (a), azimuth (A))
def Topocentric(RG, RS, Lat, ST0):
    # Radians Conversion
    Th = ST0*math.pi/180.0
    Ph = Lat*math.pi/180.0
    # Positional vector
    R = [[RS[0] - RG[0]], [RS[1] - RG[1]], [RS[2] - RG[2]]]
    # Matrix of transformation Geocentric to Topocentric
    GtoT = [[(-math.sin(Th)), (math.cos(Th)), 0],
            [-(math.sin(Ph)*math.cos(Th)), -(math.sin(Ph)*math.sin(Th)), (math.cos(Ph))],
            [(math.cos(Ph)*math.cos(Th)), (math.cos(Ph)*math.sin(Th)), (math.sin(Ph))]]
    # Conversion to tropocentric frame
    RTrop = np.matmul(GtoT, R)
    return np.array([RTrop[0], RTrop[1], RTrop[2]])

################################################################################
# Function to calculate the elevation and azimtuh angle, the input is the vector
# reference to topocentric and the outputs is the distance, elevation and
# azimuth
def Angles(Coor):
    # Return distance to ground station
    Dist = np.linalg.norm(Coor)
    # Normalize the vector to calculate elevation and azimuth angle
    RTrop = (1/(np.linalg.norm(Coor)))*Coor
    # Calculate elevation angle
    a = (math.asin(RTrop[2]))*180.0/math.pi
    # Protection cases, angles near to pi/2
    if (abs(a - 90.0) < 0.01):
        # No azimuth angle
        A = 0.0
    else:
        # To calculate the quadrant of angle, we need the signs of cosA and sinA
        sinA = (RTrop[0]/math.cos(a*math.pi/180.0))
        cosA = (RTrop[1]/math.cos(a*math.pi/180.0))
        # First value, but without quadrant
        A = (180.0/math.pi)*(math.acos(cosA))
        # Check the quadrant
        # First quadrant
        if ((sinA >= 0) and (cosA >= 0)):
            A = A
        # Second quadrant
        elif ((sinA >= 0) and (cosA <= 0)):
            A = A
        # Third quadrant
        elif ((sinA <= 0) and (cosA <= 0)):
            A = 360.0 - A
        # Fourth quadrant
        else:
            A = 360.0 - A
    # return the array of distance, elevation and azimuth
    Angles = np.array([Dist, a, A])
    return Angles

################################################################################
# Function to search and save the useful days to track the satellite. The input
# is the sweep time to search the satellite, the latitude, longitude and elevation
# of the ground station and the two format lines of the cubesat. The time simulation
# is each 1 minute.
def Search(Days, Lat, Long, Elev, line1, line2):
    T0 = datetime.datetime.utcnow()
    cubesat = twoline2rv(line1, line2, wgs72)
    for i in range(0, math.trunc(1440*Days)):
        T0 = T0 + datetime.timedelta(seconds=60)
        # Save the position and velocity (geocentric) of the cubesat
        PSat, VSat =  cubesat.propagate(T0.year, T0.month, T0.day, T0.hour,
                                        T0.minute, T0.second)
        # Calculation of sideral time for the position of Ground station each time
        STt0 = SidTime(JulianDay(T0.year, T0.month, T0.day), Long, T0.hour, T0.minute,T0.second)
        Ground0 = Geocentric(Lat, STt0, Elev)
        Sat0 = np.array([PSat[0], PSat[1], PSat[2]])
        # Conversion to trocentric-horizon frame
        R = Topocentric(Ground0, Sat0, Lat, STt0)
        # Calculate the angles to track
        A = Angles(R)
        # Now search the first positive elevation
        if A[1] > 0:
            print "Sighting for range " + str(A[0]) + " km" + " by: "
            local = T0 - datetime.timedelta(hours = 5)
            print local
