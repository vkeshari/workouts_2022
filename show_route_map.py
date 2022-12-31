import pickle

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as mpimg
import matplotlib.animation as anim

from datetime import date, timedelta

IN_FILENAME = 'pts_to_dates.data'

BASEMAP_FILENAME = 'sf_basemap.png'
CUT_BASEMAP_FILENAME = 'sf_basemap_cut.png'

OUT_MAP_FILENAME = 'sf_map.png'

IMAGE_DPI = 80
IMAGE_SIZE = 13.5 * 2

IMAGERY = cimgt.OSM(desired_tile_form = 'L')

LON_MIN = -122.52
LON_MAX = -122.37
LAT_MIN = 37.72
LAT_MAX = 37.83
LIMITS_TUPLE = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
LAT_LON_RATIO = 1.2625

DATA_BY_DAY_FILENAME = 'dates_to_ptval.data'
OUT_ANIMATION_FILENAME = 'sf_map_animated.mp4'
ANIMATION_MIN_DATE = date(2021, 1, 1)
ANIMATION_MAX_DATE = date(2023, 1, 1)
ANIMATION_FPS = 30
ONE_DAY = timedelta(days=1)

def build_base_map():
  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
  ax = fig.add_subplot(1, 1, 1, projection = IMAGERY.crs, frameon=False)
  ax.set_extent(LIMITS_TUPLE, crs = ccrs.PlateCarree())
  [s.set_visible(False) for s in ax.spines.values()]
  ax.add_image(IMAGERY, 14, cmap = 'Greys_r', alpha = 1.0)
  fig.tight_layout()
  fig.savefig(BASEMAP_FILENAME, dpi = IMAGE_DPI)
  print ("Basemap written to " + BASEMAP_FILENAME)

def build_static_map():
  basemap = mpimg.imread(CUT_BASEMAP_FILENAME)
  print ("Basemap read from " + CUT_BASEMAP_FILENAME)
  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
  ax = fig.add_subplot(1, 1, 1)
  ax.imshow(basemap, extent = LIMITS_TUPLE, aspect = LAT_LON_RATIO, alpha = 1.0)

  with open(IN_FILENAME, 'rb') as f:
    pts_to_dates = pickle.load(f)
    print("Route data read from {}".format(IN_FILENAME))

  xs = []
  ys = []
  vals = []

  for (lon, lat), dates in pts_to_dates.items():
    if lon < LON_MIN or lon > LON_MAX or lat < LAT_MIN or lat > LAT_MAX:
      continue
    xs.append(lon)
    ys.append(lat)
    vals.append(len(dates))

  hexplot = ax.hexbin(x = xs, y = ys, C = vals, gridsize = 300,
                      cmap = 'gist_earth_r', alpha = 0.9, linewidths = 0,
                      norm = colors.LogNorm(vmin = 0.5, vmax = 500))
  cbar = plt.colorbar(hexplot,
                      shrink = 0.75, aspect = 50,
                      format = "%d", pad = 0.01,
                      ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500])
  cbar.ax.tick_params(labelsize = 50)
  cbar.set_label("No. of Days", size = 50)

  plt.title("Walking in San Francisco 2021-22", fontsize = 80)
  plt.tick_params(left = False, right = False, labelleft = False,
                  labelbottom = False, bottom = False)

  #plt.show()
  fig.tight_layout()
  fig.savefig(OUT_MAP_FILENAME, dpi = IMAGE_DPI)
  print ("Map written to " + OUT_MAP_FILENAME)

def build_dynamic_map(rebuild_animation_data = True):
  basemap = mpimg.imread(CUT_BASEMAP_FILENAME)
  print ("Basemap read from " + CUT_BASEMAP_FILENAME)
  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)

  if rebuild_animation_data:
    with open(IN_FILENAME, 'rb') as f:
      pts_to_dates = pickle.load(f)
      print("Route data read from {}".format(IN_FILENAME))

    print ("Total points: " + str(len(pts_to_dates)))

    date_to_ptvals = {}
    n = 0

    for (lon, lat), dates in pts_to_dates.items():
      n += 1
      if lon < LON_MIN or lon > LON_MAX or lat < LAT_MIN or lat > LAT_MAX:
        continue
      for date in dates:
        d = date
        while d < ANIMATION_MAX_DATE:
          if d not in date_to_ptvals:
            date_to_ptvals[d] = {}
          if (lon, lat) not in date_to_ptvals[d]:
            date_to_ptvals[d][(lon, lat)] = 0
          date_to_ptvals[d][(lon, lat)] += 1
          d += ONE_DAY

      #print ("Processed " + "(" + str(lon) + ", " + str(lat) + ")" + " with no. of days: " + str(len(dates)))
      if n % 1000 == 0:
        print ("Processed " + str(n) + " points")

    with open(DATA_BY_DAY_FILENAME, 'wb+') as f:
      pickle.dump(date_to_ptvals, f)
      print("Animated route data written to {}".format(DATA_BY_DAY_FILENAME))

  with open(DATA_BY_DAY_FILENAME, 'rb') as f:
    date_to_ptvals = pickle.load(f)
    print("Animated route data read from {}".format(DATA_BY_DAY_FILENAME))

  moviewriter = anim.FFMpegWriter(fps = ANIMATION_FPS)
  with moviewriter.saving(fig, OUT_ANIMATION_FILENAME, dpi = IMAGE_DPI):
    d = ANIMATION_MIN_DATE
    while d < ANIMATION_MAX_DATE:
      print (str(d) + " has No. of points: " + str(len(date_to_ptvals[d])))

      xs = []
      ys = []
      vals = []
      for (lon, lat), val in date_to_ptvals[d].items():
        xs.append(lon)
        ys.append(lat)
        vals.append(val)

      ax = fig.add_subplot(1, 1, 1)
      fig.tight_layout()

      ax.imshow(basemap, extent = LIMITS_TUPLE, aspect = LAT_LON_RATIO, alpha = 1.0)

      hexplot = ax.hexbin(x = xs, y = ys, C = vals, gridsize = 300,
                          cmap = 'gist_earth_r', alpha = 0.9, linewidths = 0,
                          norm = colors.LogNorm(vmin = 0.5, vmax = 500))

      cbar = plt.colorbar(hexplot,
                          shrink = 0.75, aspect = 50,
                          format = "%d", pad = 0.01,
                          ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500])
      cbar.ax.tick_params(labelsize = 50)
      cbar.set_label("No. of Days", size = 50)

      ax.text(-122.40, 37.825, d.isoformat(), fontsize = 50)

      plt.title("Walking in San Francisco 2021-22", fontsize = 80)
      plt.tick_params(left = False, right = False, labelleft = False,
                      labelbottom = False, bottom = False)

      moviewriter.grab_frame()
      d += ONE_DAY

  print ("Animation written to " + OUT_ANIMATION_FILENAME)

#build_base_map() # needs cropping
#build_static_map()
build_dynamic_map(rebuild_animation_data = True)
