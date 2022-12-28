import pickle

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import matplotlib.pyplot as plt

IN_FILENAME = 'pts_to_dates.data'
OUT_MAP_FILENAME = 'sf_map.png'
IMAGE_DPI = 80
IMAGE_SIZE = 13.5

with open(IN_FILENAME, 'rb') as f:
  pts_to_dates = pickle.load(f)
  print("Route data read from {}".format(IN_FILENAME))

IMAGERY = cimgt.OSM(desired_tile_form = 'L')

fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
ax = fig.add_subplot(1, 1, 1, projection = IMAGERY.crs)
ax.set_extent([-122.52, -122.37, 37.72, 37.85], crs = ccrs.PlateCarree())
ax.add_image(IMAGERY, 14, cmap = 'Greys_r', alpha = 1.0)

xs = []
ys = []
vals = []

for (lon, lat), dates in pts_to_dates.items():
  xs.append(lon)
  ys.append(lat)
  vals.append(dates)

ax.scatter(x = xs, y = ys, s = 5.0,
            marker = 's', c = vals, cmap = 'terrain_r',
            vmin = 0, vmax = 100, alpha = 0.5,
            transform = ccrs.PlateCarree())

plt.show()
fig.savefig(OUT_MAP_FILENAME, dpi = IMAGE_DPI)
print ("Map written to " + OUT_MAP_FILENAME)
