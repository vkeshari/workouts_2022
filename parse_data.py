import os
import pickle
import xml.etree.ElementTree as ET
from datetime import date

PRECISION = 4
PRECISION_FMT = "%." + str(PRECISION) + "f"
OFFSET = pow(10.0, -PRECISION) / 2
ROUTE_DATA_DIR = '../apple_health_export/workout-routes'

pts_to_dates = {}

for f in sorted(os.listdir(ROUTE_DATA_DIR)):
  tree = ET.parse(ROUTE_DATA_DIR + '/' + f)
  root = tree.getroot()

  time_string = root[0][0].text
  d = date.fromisoformat(time_string[:10])

  for p in root[1][1]:
    (lon, lat) = (eval(PRECISION_FMT % eval(p.attrib['lon'])) + OFFSET, eval(PRECISION_FMT % eval(p.attrib['lat'])) + OFFSET)
    ele = eval(p[0].text)

    if (lon, lat) not in pts_to_dates:
      pts_to_dates[(lon, lat)] = 1
    else:
      pts_to_dates[(lon, lat)] += 1

  print(f + '\t' + 'Total points: ' + str(len(pts_to_dates)))

OUT_FILENAME = 'pts_to_dates.data'
with open('pts_to_dates.data', 'wb+') as f:
  pickle.dump(pts_to_dates, f)
  print("Route data written to {}".format(OUT_FILENAME))
