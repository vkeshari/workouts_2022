import numpy as np
import pickle

import matplotlib.pyplot as plt
import matplotlib.colors as colors

from datetime import date, timedelta
from dataclasses import dataclass

ACTIVITY_DATE_FILENAME = 'date_to_activity.data'

MIN_DATE = date(2021, 1, 1)
MAX_DATE = date(2023, 1, 1)

@dataclass
class ActivityGraphParams:
  MIN_ACTIVITY: int
  MAX_ACTIVITY: int
  BIN_WIDTH_ACTIVITY: int
  X_TICK_OFFSET: int
  MAX_VAL: int
  BIN_WIDTH_VAL: int

  X_LIMS: list[int]
  Y_LIMS: list[int]
  ACTIVITY_BINS: list[int]
  X_TICKS: list[int]
  Y_TICKS: list[int]

  TEXT_HEIGHT_T1: list[int]
  TEXT_HEIGHT_T2: list[int]
  TEXT_HEIGHT_T3: list[int]
  TEXT_HEIGHT_T4: list[int]
  TEXT_OFFSET_X: int
  TEXT_OFFSET_Y: int
  TEXT_FMT: str

  def __init__(self, min_activity, max_activity, bin_width_activity, max_val, bin_width_val,
                text_height_t1, text_height_t2, text_height_t3, text_height_t4,
                text_offset_x, text_offset_y, text_fmt):
    self.MIN_ACTIVITY = min_activity
    self.MAX_ACTIVITY = max_activity
    self.BIN_WIDTH_ACTIVITY = bin_width_activity
    self.X_TICK_OFFSET = int(bin_width_activity / 2)
    self.MAX_VAL = max_val
    self.BIN_WIDTH_VAL = bin_width_val

    self.X_LIMS = [min_activity, max_activity]
    self.Y_LIMS = [0, max_val]
    self.ACTIVITY_BINS = [v for v in range(min_activity, max_activity + 1, bin_width_activity)]
    self.X_TICKS = [v for v in range(min_activity + self.X_TICK_OFFSET, max_activity + self.X_TICK_OFFSET, bin_width_activity)]
    self.Y_TICKS = [v for v in range(0, max_val + 1, bin_width_val)]

    self.TEXT_HEIGHT_T1 = text_height_t1
    self.TEXT_HEIGHT_T2 = text_height_t2
    self.TEXT_HEIGHT_T3 = text_height_t3
    self.TEXT_HEIGHT_T4 = text_height_t4
    self.TEXT_OFFSET_X = text_offset_x
    self.TEXT_OFFSET_Y = text_offset_y
    self.TEXT_FMT = text_fmt

energy_graph_params = ActivityGraphParams(min_activity = 750, max_activity = 2250, bin_width_activity = 100,
                                          max_val = 100, bin_width_val = 10,
                                          text_height_t1 = [80, 85],
                                          text_height_t2 = [70, 75],
                                          text_height_t3 = [60, 65],
                                          text_height_t4 = [50, 55],
                                          text_offset_x = 10, text_offset_y = 1,
                                          text_fmt = "%d")

distance_graph_params = ActivityGraphParams(min_activity = 3, max_activity = 20, bin_width_activity = 1,
                                            max_val = 100, bin_width_val = 10,
                                            text_height_t1 = [80, 85],
                                            text_height_t2 = [70, 75],
                                            text_height_t3 = [60, 65],
                                            text_height_t4 = [50, 55],
                                            text_offset_x = 0.1, text_offset_y = 1,
                                            text_fmt = "%.1f")

stand_graph_params = ActivityGraphParams(min_activity = 110, max_activity = 450, bin_width_activity = 20,
                                          max_val = 100, bin_width_val = 10,
                                          text_height_t1 = [80, 85],
                                          text_height_t2 = [70, 75],
                                          text_height_t3 = [60, 65],
                                          text_height_t4 = [50, 55],
                                          text_offset_x = 2, text_offset_y = 1,
                                          text_fmt = "%d")

graph_params = {}
graph_params['energy'] = energy_graph_params
graph_params['distance'] = distance_graph_params
graph_params['stand'] = stand_graph_params

COLOR_2021 = 'tab:blue'
COLOR_2022 = 'tab:orange'

IMAGE_DPI = 80
IMAGE_SIZE = 13.5 * 2

OUT_GRAPH_FILENAME_SUFFIX = '_graph.png'

def read_activity_data():
  with open(ACTIVITY_DATE_FILENAME, 'rb') as f:
    date_to_activity = pickle.load(f)
    print("Activity data read from {}".format(ACTIVITY_DATE_FILENAME))

  return date_to_activity

def add_marker(ax, metric, label, buckets, values, heights, colors):
  for i in range(len(values)):
    ax.plot([values[i], values[i]], [0, heights[i]],
            alpha = 0.8, linewidth = 10, linestyle = 'dashed', color = colors[i])
    ax.text(values[i] + graph_params[metric].TEXT_OFFSET_X, heights[i] + graph_params[metric].TEXT_OFFSET_Y,
            buckets[i] + " " + label + ": " + graph_params[metric].TEXT_FMT % values[i], fontsize = 40, color = colors[i])

def show_activity_graphs(date_to_activity, metric, text):
  year_to_activity = {}
  for d, energy in date_to_activity[metric].items():
    if d < MIN_DATE or d >= MAX_DATE:
      continue
    if d.year not in year_to_activity:
      year_to_activity[d.year] = []
    year_to_activity[d.year].append(energy)

  fig = plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE), dpi = IMAGE_DPI)
  ax = fig.add_subplot(1, 1, 1)

  hist_2021 = ax.hist(year_to_activity[2021], bins = graph_params[metric].ACTIVITY_BINS,
                      alpha = 0.4, label = '2021 (WFH)', color = COLOR_2021)
  hist_2022 = ax.hist(year_to_activity[2022], bins = graph_params[metric].ACTIVITY_BINS,
                      alpha = 0.4, label = '2022 (Commute)', color = COLOR_2022)
  ax.set_xlim(graph_params[metric].X_LIMS)
  ax.set_ylim(graph_params[metric].Y_LIMS)

  avg_2021 = np.average(year_to_activity[2021])
  avg_2022 = np.average(year_to_activity[2022])
  add_marker(ax, metric = metric, label = 'Average',
              buckets = ['2021', '2022'], values = [avg_2021, avg_2022],
              heights = graph_params[metric].TEXT_HEIGHT_T2,
              colors = [COLOR_2021, COLOR_2022])

  p50_2021 = np.percentile(year_to_activity[2021], 50)
  p50_2022 = np.percentile(year_to_activity[2022], 50)
  add_marker(ax, metric = metric, label = 'Median',
              buckets = ['2021', '2022'], values = [p50_2021, p50_2022],
              heights = graph_params[metric].TEXT_HEIGHT_T1,
              colors = [COLOR_2021, COLOR_2022])

  p95_2021 = np.percentile(year_to_activity[2021], 95)
  p95_2022 = np.percentile(year_to_activity[2022], 95)
  add_marker(ax, metric = metric, label = '95p',
              buckets = ['2021', '2022'], values = [p95_2021, p95_2022],
              heights = graph_params[metric].TEXT_HEIGHT_T3,
              colors = [COLOR_2021, COLOR_2022])

  plt.legend(loc = 'upper right', fontsize = 60)
  plt.title('No. of Days by ' + text, fontsize = 80)
  plt.xlabel(text + ' -->', fontsize = 60)
  plt.ylabel('No. of Days -->', fontsize = 60)
  plt.xticks(graph_params[metric].X_TICKS, rotation = 45)
  plt.yticks(graph_params[metric].Y_TICKS)
  plt.tick_params(labelsize = 40)
  plt.grid(which = 'both', axis = 'both')

  fig.tight_layout()
  fig.savefig(metric + OUT_GRAPH_FILENAME_SUFFIX)

date_to_activity = read_activity_data()

show_activity_graphs(date_to_activity = date_to_activity, metric = 'energy', text = 'Active Calories Burned')
show_activity_graphs(date_to_activity = date_to_activity, metric = 'distance', text = 'Distance Walked (Miles)')
show_activity_graphs(date_to_activity = date_to_activity, metric = 'stand', text = 'Minutes Spent Standing')
