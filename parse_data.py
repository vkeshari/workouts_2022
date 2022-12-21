import os
import pickle
import xml.etree.ElementTree as ET
from datetime import date

PRECISION_FMT = "%.4f"
DATA_DIR = '../apple_health_export/workout-routes'

for f in sorted(os.listdir(DATA_DIR)):
  tree = ET.parse(DATA_DIR + '/' + f)
  root = tree.getroot()

  time_string = root[0][0].text
  d = date.fromisoformat(time_string[:10])

  pts_to_dates = {}

  for p in root[1][1]:
    (lon, lat) = (PRECISION_FMT % eval(p.attrib['lon']), PRECISION_FMT % eval(p.attrib['lat']))
    ele = eval(p[0].text)

    if (lon, lat) not in pts_to_dates:
      pts_to_dates[(lon, lat)] = {d}
    else:
      pts_to_dates[(lon, lat)].add(d)

  print(f + '\t' + str(len(pts_to_dates)) + " points")

OUT_FILENAME = 'pts_to_dates.data'
with open('pts_to_dates.data', 'wb+') as f:
  pickle.dump(pts_to_dates, f)
  print("Data written to {}".format(OUT_FILENAME))
