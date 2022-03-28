# SVK 03/22/22
# Code from https://wrf-python.readthedocs.io/en/latest/plot.html
# Modified to use for case studies of FY21 OD days.
# 

import os
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import cartopy.crs as crs
from cartopy.feature import NaturalEarthFeature
from wrf import (getvar, interplevel, to_np, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim)

# Open the NetCDF file
#WRFname = "C:\wrfout_d04_2021-09-01_20.hdf5"
os.chdir('.\\data') 
WRFname = 'wrfout_d04_2021-09-01_21%3A00%3A00'
ncfile = Dataset(WRFname)

# Extract the pressure, geopotential height, and wind variables
p = getvar(ncfile, "pressure")
slp = getvar(ncfile, "slp", units="mb")
z = getvar(ncfile, "z", units="dm")
ua = getvar(ncfile, "ua", units="kt")
va = getvar(ncfile, "va", units="kt")

u10 = getvar(ncfile, "uvmet10", units="kt") [0,:]
v10 = getvar(ncfile, "uvmet10", units="kt") [1,:]

wspd = getvar(ncfile, "wspd_wdir", units="kts")[0,:]
hgt = getvar(ncfile, "HGT") # test to get terrrain

# Get the lat/lon coordinates
lats, lons = latlon_coords(u10)

# Get the map projection information
cart_proj = get_cartopy(u10)

# Create the figure
fig = plt.figure(figsize=(12,9))
ax = plt.axes(projection=cart_proj)

# Add TTU and WX Bldg points
plt.plot(to_np(-112.937),to_np(41.053), 'ok', markersize=6,transform=crs.PlateCarree())
plt.text(to_np(-112.937),to_np(41.053), 'WX_Bldg', fontsize=12, fontweight='heavy',transform=crs.PlateCarree())

plt.plot(to_np(-112.897),to_np(41.131), 'ok', markersize=6,transform=crs.PlateCarree())
plt.text(to_np(-112.897),to_np(41.131), 'TTU', fontsize=12, fontweight='heavy',transform=crs.PlateCarree())

# Add terrain height
levels = np.arange(1300., 2600, 50)
terrain_contours = plt.contourf(to_np(lons),to_np(lats), to_np(hgt),
                               levels=levels,
                               cmap=get_cmap('terrain'), 
                               transform=crs.PlateCarree())

# Add the surface level pressure contours
levels = np.arange(980., 1050., 2)
contours = plt.contour(to_np(lons), to_np(lats), to_np(slp),
                       levels=levels, colors="black",
                       transform=crs.PlateCarree())
plt.clabel(contours, inline=1, fontsize=10, fmt="%i")

# Add the surface wind barbs, only plotting every 5th data point.
plt.barbs(to_np(lons[::8,::8]), to_np(lats[::8,::8]),
          to_np(u10[::8,::8]), to_np(v10[::8,::8]),
          transform=crs.PlateCarree(), length=6)

# Set the map bounds
ax.set_xlim(cartopy_xlim(slp))
ax.set_ylim(cartopy_ylim(slp))

ax.gridlines()

plt.title("Sea Level Pressure (mb), Surface Wind Speed (kt)")

#filename = WRFname.split('.')[0]
#strings=[filename[0],'_800mb.jpg']
#filename = ''.join(strings)
#filename = ''.join([WRFname.split('.')[0],'_800mb.png'])

plt.savefig(''.join([WRFname[:-5],'_slp.png']))

plt.show()

## pull surface variables

