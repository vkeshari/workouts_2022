import os
import pickle
import xml.etree.ElementTree as ET
from datetime import date

PRECISION = 4
PRECISION_FMT = "%." + str(PRECISION) + "f"
OFFSET = pow(10.0, -PRECISION) / 2
ROUTE_DATA_DIR = '../apple_health_export/workout-routes'

LON_MIN = -122.52
LON_MAX = -122.37
LAT_MIN = 37.72
LAT_MAX = 37.83

MIN_DATE = date(2021, 1, 1)
MAX_DATE = date(2023, 1, 1)

pts_to_dates = {}

for f in sorted(os.listdir(ROUTE_DATA_DIR)):
  tree = ET.parse(ROUTE_DATA_DIR + '/' + f)
  root = tree.getroot()

  time_string = f[6:16]
  d = date.fromisoformat(time_string[:10])
  if d < MIN_DATE or d >= MAX_DATE:
    continue

  for p in root[1][1]:
    (lon, lat) = (eval(PRECISION_FMT % eval(p.attrib['lon'])) + OFFSET, eval(PRECISION_FMT % eval(p.attrib['lat'])) + OFFSET)
    ele = eval(p[0].text)
    
    if lon < LON_MIN or lon > LON_MAX or lat < LAT_MIN or lat > LAT_MAX:
      continue

    if (lon, lat) not in pts_to_dates:
      pts_to_dates[(lon, lat)] = {d}
    else:
      pts_to_dates[(lon, lat)].add(d)

  print(f + '\t' + 'Total points: ' + str(len(pts_to_dates)))

OUT_FILENAME = 'pts_to_dates.data'
with open(OUT_FILENAME, 'wb+') as f:
  pickle.dump(pts_to_dates, f)
  print("Route data written to {}".format(OUT_FILENAME))
