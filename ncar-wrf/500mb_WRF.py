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
slp = getvar(ncfile, "slp")
z = getvar(ncfile, "z", units="dm")
ua = getvar(ncfile, "ua", units="kt")
va = getvar(ncfile, "va", units="kt")

u10 = getvar(ncfile, "uvmet10", units="kt") [0,:]
v10 = getvar(ncfile, "uvmet10", units="kt") [:,0]

wspd = getvar(ncfile, "wspd_wdir", units="kts")[0,:]
hgt = getvar(ncfile, "HGT") # test to get terrrain

# Interpolate geopotential height, u, and v winds to 500 hPa
ht_500 = interplevel(z, p, 500)
u_500 = interplevel(ua, p, 500)
v_500 = interplevel(va, p, 500)
wspd_500 = interplevel(wspd, p, 500)

# Get the lat/lon coordinates
lats, lons = latlon_coords(ht_500)

# Get the map projection information
cart_proj = get_cartopy(ht_500)

# Create the figure
fig = plt.figure(figsize=(12,9))
ax = plt.axes(projection=cart_proj)

# Add terrain height
levels = np.arange(1300., 4000.,1000)
terrain_contours = plt.contour(to_np(lons),to_np(lats), to_np(hgt),
                               levels=levels,colors="black", 
                               transform=crs.PlateCarree())

# Add the 500 hPa geopotential height contours
levels = np.arange(550., 600., 2.)
contours = plt.contour(to_np(lons), to_np(lats), to_np(ht_500),
                       levels=levels, colors="black",
                       transform=crs.PlateCarree())
plt.clabel(contours, inline=1, fontsize=10, fmt="%i")

# Add the wind speed contours
levels = np.arange(5., 50., 2.5)
wspd_contours = plt.contourf(to_np(lons), to_np(lats), to_np(wspd_500),
                             levels=levels,
                             cmap=get_cmap("rainbow"),
                             transform=crs.PlateCarree())
plt.colorbar(wspd_contours, ax=ax, orientation="horizontal", pad=.05)

# Add the 500 hPa wind barbs, only plotting every 10th data point.
plt.barbs(to_np(lons[::10,::10]), to_np(lats[::10,::10]),
          to_np(u_500[::10,::10]), to_np(v_500[::10,::10]),
          transform=crs.PlateCarree(), length=6)

# Set the map bounds
ax.set_xlim(cartopy_xlim(ht_500))
ax.set_ylim(cartopy_ylim(ht_500))

ax.gridlines()

plt.title("500 MB Height (dm), Wind Speed (kt), Barbs (kt)")

# Add TTU and WX Bldg points
plt.plot(to_np(-112.937),to_np(41.053), 'ok', markersize=6,transform=crs.PlateCarree())
plt.text(to_np(-112.937),to_np(41.053), 'WX_Bldg', fontsize=12, fontweight='heavy',transform=crs.PlateCarree())

plt.plot(to_np(-112.897),to_np(41.131), 'ok', markersize=6,transform=crs.PlateCarree())
plt.text(to_np(-112.897),to_np(41.131), 'TTU', fontsize=12, fontweight='heavy',transform=crs.PlateCarree())

#filename = WRFname.split('.')[0]
#strings=[filename[0],'_500mb.jpg']
#filename = ''.join(strings)
#filename = ''.join([WRFname.split('.')[0],'_500mb.png'])

plt.savefig(''.join([WRFname[:-5],'_500mb.png']))

plt.show()

## pull surface variables

