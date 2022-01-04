# WRF Simple Sounding from: https://pratiman-91.github.io/2021/08/05/SkewT-Plots-from-WRF-outputs.html
# SVK 12/29/21-1/2/22
# Trying to use the wrf module for python. Does this interpolate better/easier than extract_sounding_data.py?
# Make sure we are extracting the most appropriate data before putting it into FDTD. Be able to 
# plot any of this data in order to perform real-world comparisons.

#from logging import _srcfile
import wrf
from netCDF4 import Dataset
import matplotlib.pyplot as plt

import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units

import pandas as pd

import numpy as np
from shapely.geometry import Point
from collections import namedtuple
import os
import re
import datetime

# Load the WRF file and requested variables

wrfin = Dataset(r"C:\wrfout_d04_2021-09-01_20.hdf5")
src_file = "C:\wrfout_d04_2021-09-01_20.hdf5"

p1 = wrf.getvar(wrfin,"pressure",timeidx=0)
T1 = wrf.getvar(wrfin,"tc",timeidx=0)
Td1 = wrf.getvar(wrfin,"td",timeidx=0)
u1 = wrf.getvar(wrfin,"ua",timeidx=0)
v1 = wrf.getvar(wrfin,"va",timeidx=0)
uvm1 = wrf.getvar(wrfin,"uvmet",timeidx=0)
z1 = wrf.getvar(wrfin,"z",timeidx=0)
T2m1 = wrf.getvar(wrfin,"T2",timeidx=0)
Td2m1 = wrf.getvar(wrfin,"td2",timeidx=0)

umet1 = uvm1[0,:,:,:]
vmet1 = uvm1[1,:,:,:]
ws1 = mpcalc.wind_speed(umet1,vmet1)
wdir1 = mpcalc.wind_direction(umet1,vmet1,convention='from')

# Get the XY values from the lat/long and extract nearest values from variables
#SVK put in a loop here

WBlat_lon = [41.0530920, -112.9368890, 1349]
TTUlat_lon = [41.131, -112.8965, 1446]

x_y = wrf.ll_to_xy(wrfin, WBlat_lon[0], WBlat_lon[1])
x_yTTU = wrf.ll_to_xy(wrfin, TTUlat_lon[0], TTUlat_lon[1])
#print(x_y, "x_y_printed")
#print(x_yTTU, "x_yTTU printed")

lat_lon__WB = wrf.xy_to_ll(wrfin, x_y[0],x_y[1],timeidx=0)
#print(lat_lon__WB, "lat and lon of the WB from x-y")
#input("Press Enter to continue")

p = p1[:,x_y[0],x_y[1]] * units.hPa
T = T1[:,x_y[0],x_y[1]] * units.degC
Td = Td1[:,x_y[0],x_y[1]] * units.degC
u = v1[:,x_y[0],x_y[1]] * units('m/s')
v = u1[:,x_y[0],x_y[1]] * units('m/s')
z = z1[:,x_y[0],x_y[1]] * units('m')
T2 = T2m1[x_y[0],x_y[1]] * units.degC
Td2 = Td2m1[x_y[0],x_y[1]] * units.degC

ws = ws1[:,x_y[0],x_y[1]] * units('m/s')
wdir = wdir1[:,x_y[0],x_y[1]] * units('deg')

# create a df of all params
selectedDf = pd.DataFrame({"pressure":p, "temperature": T, "dew_point":Td, "wind_dir":wdir, "wind_speed": ws, "elevation": z})
 
filename =  f'{os.path.basename(src_file)}_WxBldg_300K.txt'

filepath = os.path.join(r"C:\Users\svankloo\Source-svkcode", filename)
filedatestr = re.search("[\d][\d][\d][\d]-[\d][\d]-[\d][\d]_[\d][\d]",filename)[0]
file_datetime = datetime.datetime.strptime(filedatestr, "%Y-%m-%d_%H")

with open(filepath, 'w') as fle:
    fle.write(f"RAOB/CSV, {filename}\n")
    fle.write("INFO:1, First line of freeform text\n")
    fle.write("INFO:2, Another freeform text line\n")
    fle.write(f"DTG, {file_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
    fle.write(f"LAT, {WBlat_lon[0]}, N\n")
    fle.write(f"LON, {WBlat_lon[1]}, W\n")
    fle.write(f"ELEV, {1349}, M\n")
    fle.write("TEMPERATURE, C\n")
    fle.write("MOISTURE, TD\n")
    fle.write("WIND, m/s\n")
    fle.write("GPM, MSL, M\n")
    fle.write("MISSING, -999\n")
    fle.write("SORT, YES\n")
    fle.write("RAOB/DATA\n")
    fle.write("PRES, TEMP, TD, WIND, SPEED, GPM\n")
    for i, r in selectedDf.iterrows():
        fle.write(f"{round(r.pressure)}, {round(r.temperature)}, {r.dew_point:.1f}, {round(r.wind_dir)}, {r.wind_speed:.1f}, {round(r.elevation)}\n")

skew = SkewT()

# Plot the data using normal plotting functions, in this case using
# log scaling in Y, as dictated by the typical meteorological plot
skew.plot(p, T, 'r')
skew.plot(p, Td, 'g')
skew.plot_barbs(p, u, v)

# Add the relevant special lines
skew.plot_dry_adiabats()
skew.plot_moist_adiabats()
skew.plot_mixing_lines()
skew.ax.set_xlim(-60, 40)
skew.ax.set_xlabel('Temperature ($^\circ$C)')
skew.ax.set_ylabel('Pressure (hPa)')

plt.savefig('SkewT_Simplesvk.png', bbox_inches='tight')
