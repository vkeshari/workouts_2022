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
OUT_MAP_DIRNAME = 'route_maps'

IMAGE_DPI = 80
IMAGE_SIZE = 13.5 * 2

IMAGERY = cimgt.OSM(desired_tile_form = 'L')

LON_MIN = -122.52
LON_MAX = -122.37
LAT_MIN = 37.72
LAT_MAX = 37.83
LIMITS_TUPLE = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
LAT_LON_RATIO = 1.2625 # at latitude 37.75 N

OUT_ANIMATION_FILENAME = 'sf_map_animated.mp4'
ANIMATION_MIN_DATE = date(2021, 1, 1)
ANIMATION_MAX_DATE = date(2023, 1, 1)
ANIMATION_FPS = 12
LAST_FRAME_PAD = 5 * ANIMATION_FPS # 5 seconds

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

def build_static_map(start_date = ANIMATION_MIN_DATE, end_date_inclusive = ANIMATION_MAX_DATE - ONE_DAY,
                      out_filename = OUT_MAP_FILENAME, pts_to_dates = None,
                      show_fig = True, show_debug = True):
  basemap = mpimg.imread(CUT_BASEMAP_FILENAME)
  if show_debug:
    print ("Basemap read from " + CUT_BASEMAP_FILENAME)
  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
  ax = fig.add_subplot(1, 1, 1)
  ax.imshow(basemap, extent = LIMITS_TUPLE, aspect = LAT_LON_RATIO, alpha = 1.0)

  if not pts_to_dates:
    with open(IN_FILENAME, 'rb') as f:
      pts_to_dates = pickle.load(f)
      if show_debug:
        print("Route data read from {}".format(IN_FILENAME))

  xs = []
  ys = []
  vals = []

  for (lon, lat), dates in pts_to_dates.items():
    if lon < LON_MIN or lon > LON_MAX or lat < LAT_MIN or lat > LAT_MAX:
      continue
    num_d = len([d for d in dates if d >= start_date and d <= end_date_inclusive])
    xs.append(lon)
    ys.append(lat)
    vals.append(num_d)

  hexplot = ax.hexbin(x = xs, y = ys, C = vals, gridsize = 300,
                      cmap = 'gist_earth_r', alpha = 0.9, linewidths = 0,
                      norm = colors.LogNorm(vmin = 0.2, vmax = 500))
  cbar = plt.colorbar(hexplot,
                      shrink = 0.75, aspect = 50,
                      format = "%d", pad = 0.01,
                      ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500])
  cbar.ax.tick_params(labelsize = 50)
  cbar.set_label("No. of Days", size = 50)

  ax.text(-122.40, 37.825, end_date_inclusive.isoformat(), fontsize = 50)

  plt.title("Walking in San Francisco 2021-22", fontsize = 80)
  plt.tick_params(left = False, right = False, labelleft = False,
                  labelbottom = False, bottom = False)

  if show_fig:
    plt.show()
  fig.tight_layout()
  fig.savefig(out_filename, dpi = IMAGE_DPI)
  print ("Map written to " + out_filename)
  plt.close(fig)

def rebuild_route_maps(start_date = ANIMATION_MIN_DATE, end_date = ANIMATION_MAX_DATE,
                        data_start_date = ANIMATION_MIN_DATE):
  with open(IN_FILENAME, 'rb') as f:
    pts_to_dates = pickle.load(f)
    print("Route data read from {}".format(IN_FILENAME))

  d = start_date
  while d < end_date:
    route_map_filename = OUT_MAP_DIRNAME + '/' + d.isoformat() + ".png"
    build_static_map(start_date = data_start_date, end_date_inclusive = d,
                      out_filename = route_map_filename, pts_to_dates = pts_to_dates,
                      show_fig = False, show_debug = False)
    d += ONE_DAY

def build_dynamic_map(start_date = ANIMATION_MIN_DATE, end_date = ANIMATION_MAX_DATE,
                      rebuild_each_map = True, last_frame_pad = LAST_FRAME_PAD,
                      skip_animation = False):
  if rebuild_each_map:
    rebuild_route_maps(start_date = start_date, end_date = end_date, data_start_date = start_date)

  if skip_animation:
    print ("Animation skipped")
    return

  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)

  pad = last_frame_pad

  moviewriter = anim.FFMpegWriter(fps = ANIMATION_FPS)
  with moviewriter.saving(fig, OUT_ANIMATION_FILENAME, dpi = IMAGE_DPI):
    d = start_date
    while d < end_date and pad > 0:
      if d < end_date:
        route_map_filename = OUT_MAP_DIRNAME + '/' + str(d) + ".png"
      else:
        route_map_filename = OUT_MAP_DIRNAME + '/' + str(end_date - ONE_DAY) + ".png"
      route_map = mpimg.imread(route_map_filename)
      print ("Route map read from " + route_map_filename)

      ax = fig.add_subplot(1, 1, 1)
      fig.tight_layout()

      ax.imshow(route_map, extent = LIMITS_TUPLE, aspect = LAT_LON_RATIO, alpha = 1.0)

      moviewriter.grab_frame()
      ax.clear()

      if d < end_date:
        d += ONE_DAY
      else:
        pad -= 1

  print ("Animation written to " + OUT_ANIMATION_FILENAME)

#build_base_map() # needs cropping, cropped map already at sf_basemap_cut.png

#build_static_map(show_fig = False, show_debug = True)
#build_static_map(start_date = date(2021, 1, 1), end_date_inclusive = date(2021, 2, 1) - ONE_DAY, show_fig = False, show_debug = True)

#rebuild_route_maps(start_date = date(2021, 1, 1), end_date = date(2021, 7, 1), data_start_date = date(2021, 1, 1))

build_dynamic_map(rebuild_each_map = False)
#build_dynamic_map(start_date = date(2021, 1, 1), end_date = date(2021, 2, 1), rebuild_each_map = True, skip_animation = True)

