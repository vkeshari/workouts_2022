import pickle

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import matplotlib.pyplot as plt
import matplotlib.colors as colors

IN_FILENAME = 'pts_to_dates.data'
OUT_MAP_FILENAME = 'sf_map.png'
IMAGE_DPI = 80
IMAGE_SIZE = 13.5

LON_MIN = -122.52
LON_MAX = -122.37
LAT_MIN = 37.72
LAT_MAX = 37.83
LIMITS_TUPLE = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]

with open(IN_FILENAME, 'rb') as f:
  pts_to_dates = pickle.load(f)
  print("Route data read from {}".format(IN_FILENAME))

IMAGERY = cimgt.OSM(desired_tile_form = 'L')

fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
ax = fig.add_subplot(1, 1, 1, projection = IMAGERY.crs, frameon=False)
ax.set_extent(LIMITS_TUPLE, crs = ccrs.PlateCarree())
ax.add_image(IMAGERY, 14, cmap = 'Greys_r', alpha = 1.0)

xs = []
ys = []
vals = []

for (lon, lat), dates in pts_to_dates.items():
  if lon < LON_MIN or lon > LON_MAX or lat < LAT_MIN or lat > LAT_MAX:
    continue
  xs.append(lon)
  ys.append(lat)
  vals.append(dates)

hexplot = ax.hexbin(x = xs, y = ys, C = vals, gridsize = 300,
                    cmap = 'gist_earth_r', alpha = 0.8, linewidths = 0,
                    norm = colors.LogNorm(vmin = 0.5, vmax = 500),
                    transform = ccrs.PlateCarree())
cbar = plt.colorbar(hexplot,
                    shrink = 0.85, aspect = 50,
                    format = "%d", pad = 0.01,
                    ticks = [1, 2, 5, 10, 50, 100, 500])
cbar.ax.tick_params(labelsize = 20)
cbar.set_label("No. of Days", size = 20)

plt.title("Walking in San Francisco 2021-22", fontsize = 30)

plt.show()
fig.savefig(OUT_MAP_FILENAME, dpi = IMAGE_DPI)
print ("Map written to " + OUT_MAP_FILENAME)
