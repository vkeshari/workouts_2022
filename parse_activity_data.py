import pickle
from datetime import date

ACTIVITY_FILENAME = '../apple_health_export/export.xml'
ACTIVITY_CUT_FILENAME = '../apple_health_export/export_cut.xml'

ENERGY_KEYWORD = 'HKQuantityTypeIdentifierActiveEnergyBurned'
DISTANCE_KEYWORD = 'HKQuantityTypeIdentifierDistanceWalkingRunning'
STAND_KEYWORD = 'HKQuantityTypeIdentifierAppleStandTime'
KEYWORDS = {ENERGY_KEYWORD, DISTANCE_KEYWORD, STAND_KEYWORD}
EXCLUDE_KEYWORDS = {'WorkoutStatistics'}

def cut_export_file():
  fin = open(ACTIVITY_FILENAME, 'r')
  fout = open(ACTIVITY_CUT_FILENAME, 'w+')

  n = 0
  for l in fin.readlines():
    n += 1
    if n % 100000 == 0:
      print ('Line: ' + str(n))

    exclude_found = False
    for k in EXCLUDE_KEYWORDS:
      if k in l:
        exclude_found = True
        break
    if exclude_found:
      continue

    found = False
    for k in KEYWORDS:
      if k in l:
        found = True
        break
    if found:
      fout.write(l)

  fin.close()
  fout.close()

START_DATE_KEYWORD = 'startDate='
VALUE_KEYWORD = 'value='

def build_data_map():
  date_to_energy = {}
  date_to_distance = {}
  date_to_stand = {}

  n = 2
  with open(ACTIVITY_CUT_FILENAME, 'r') as f:
    for l in f.readlines()[2 : -1]:
      n += 1
      if n % 10000 == 0:
        print ("Data points: " + str(n))

      try:
        in_sd = l.find(START_DATE_KEYWORD)
        d = date.fromisoformat(l[in_sd + 11 : in_sd + 21])

        in_val = l.find(VALUE_KEYWORD)
        in_val_end = l[in_val + 7 : ].find('"')
        v = eval(l[in_val + 7 : in_val + 7 + in_val_end])
      except:
        print ("Exception at line:\t" + str(n))
        break

      if ENERGY_KEYWORD in l:
        if d not in date_to_energy:
          date_to_energy[d] = 0
        date_to_energy[d] += v
      if DISTANCE_KEYWORD in l:
        if d not in date_to_distance:
          date_to_distance[d] = 0
        date_to_distance[d] += v
      if STAND_KEYWORD in l:
        if d not in date_to_stand:
          date_to_stand[d] = 0
        date_to_stand[d] += v

  date_to_activity = {}
  date_to_activity['energy'] = date_to_energy
  date_to_activity['distance'] = date_to_distance
  date_to_activity['stand'] = date_to_stand

  OUT_FILENAME = 'date_to_activity.data'
  with open(OUT_FILENAME, 'wb+') as f:
    pickle.dump(date_to_activity, f)
    print("Activity data written to {}".format(OUT_FILENAME))

#cut_export_file()
build_data_map()
