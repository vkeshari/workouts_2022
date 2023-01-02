import numpy as np
import pickle

from datetime import date, timedelta

ACTIVITY_DATE_FILENAME = 'date_to_activity.data'

def show_activity_graphs():
  with open(ACTIVITY_DATE_FILENAME, 'rb') as f:
    date_to_activity = pickle.load(f)
    print("Activity data read from {}".format(ACTIVITY_DATE_FILENAME))

  test_date = date(2022, 12, 31)
  print (str(date_to_activity['energy'][test_date]))
  print (str(date_to_activity['distance'][test_date]))
  print (str(date_to_activity['stand'][test_date]))

show_activity_graphs()
