import pickle

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import matplotlib.pyplot as plt

IN_FILENAME = 'pts_to_dates.data'

with open(IN_FILENAME, 'rb') as f:
  pts_to_dates = pickle.load(f)
  print("Route data read from {}".format(IN_FILENAME))

IMAGERY = cimgt.OSM(desired_tile_form = 'L')

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=IMAGERY.crs)
ax.set_extent([-122.52, -122.37, 37.72, 37.85], crs=ccrs.PlateCarree())
ax.add_image(IMAGERY, 14, cmap = 'Greys_r')

plt.show()
