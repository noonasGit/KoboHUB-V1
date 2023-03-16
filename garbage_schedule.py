# By Jonas Johansson
# This code, extracts and matches garbage days for collection 
# For the KoboHUB Dashboard
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import configparser


@dataclass
class garbage_summary:
    landfill: int
    recycle:int
    compost : int
    xmas_tree: int
    landfill_prepapre : int
    recycle_prepare : int
    compost_prepare : int
    dumpster : int
    dumpster_prepapre : int

def get_garbage_config_data(file_path:str):
    parser = configparser.RawConfigParser()
    parser.read(file_path)
    data = dict()
    data['landfill_title-id'] = parser.get("landfill-schedule", "title")
    data['landfill_prepare-date-month-id'] = parser.get("landfill-schedule", "prepare-date-month")
    data['landfill_collect-date-month-id'] = parser.get("landfill-schedule", "collect-date-month")

    data['recycle_title-id'] = parser.get("recycle-schedule", "title")
    data['recycle_prepare-date-month-id'] = parser.get("recycle-schedule", "prepare-date-month")
    data['recycle_collect-date-month-id'] = parser.get("recycle-schedule", "collect-date-month")

    data['compost_title-id'] = parser.get("compost-schedule", "title")
    data['compost_prepare-date-month-id'] = parser.get("compost-schedule", "prepare-date-month")
    data['compost_collect-date-month-id'] = parser.get("compost-schedule", "collect-date-month")

    data['dumpster_title-id'] = parser.get("dumpster-schedule", "title")
    data['dumpster_prepare-date-month-id'] = parser.get("dumpster-schedule", "prepare-date-month")
    data['dumpster_collect-date-month-id'] = parser.get("dumpster-schedule", "collect-date-month")

    data['holiday-tree-schedule_title-id'] = parser.get("holiday-tree-schedule", "title")
    data['holiday-tree-schedule_collect-date-month-id'] = parser.get("holiday-tree-schedule", "collect-date-month")

    data['all-garbage-prepare-message-id'] = parser.get("all-garbage", "prepare-message")
    data['all-garbage-collect-message-id'] = parser.get("all-garbage", "collect-message")
    data['all-collection-time-over-id'] = parser.get("all-garbage", "collection-time-over")
    data['all-garbage-time-message-today-id'] = parser.get("all-garbage", "garbage-time-message-today")
    data['all-garbage-time-message-tomorrow-id'] = parser.get("all-garbage", "garbage-time-message-tomorrow")
    data['all-garbage-time-message-end-id'] = parser.get("all-garbage", "garbage-time-message-end")
    data['all-collection-time-over-message-line1-id'] = parser.get("all-garbage", "collection-time-over-message-line1")
    data['all-collection-time-over-message-line2-id'] = parser.get("all-garbage", "collection-time-over-message-line2")
    return data


def read_garbage_schedules(file_path):
   file = open(file_path, "r")
   contents = file.read()
   list_of_contents = contents.split(",")
   file.close()
   return list_of_contents

def isgarbageday(g1,g2):
  if g1 in g2 :
   return 1
  else:
   return 0

def get_garbage_status():
  # date object of today's date
  today = date.today() 
  garbage_schedule = dict()
  garbage_schedule=get_garbage_config_data("garbage_schedules.ini")

  '''
  print(garbage_schedule['landfill_title-id'])
  print(garbage_schedule['recycle_title-id'])
  print(garbage_schedule['compost_title-id'])
  print(garbage_schedule['dumpster_title-id'])
  print(garbage_schedule['holiday-tree-schedule_title-id'])
  print(garbage_schedule['all-garbage-prepare-message-id'])
  print(garbage_schedule['all-garbage-collect-message-id'])
  print(garbage_schedule['all-collection-time-over-id'])
  print(garbage_schedule['all-garbage-time-message-today-id'])
  print(garbage_schedule['all-garbage-time-message-tomorrow-id'])
  print(garbage_schedule['all-garbage-time-message-end-id'])
  print(garbage_schedule['all-collection-time-over-message-line1-id'])
  print(garbage_schedule['all-collection-time-over-message-line2-id'])
  '''

  dumpster_prepare_list = garbage_schedule['dumpster_prepare-date-month-id']
  dumpster_config = garbage_schedule['dumpster_collect-date-month-id']
  landfill_prepare_list = garbage_schedule['landfill_prepare-date-month-id']
  landfill_config = garbage_schedule['landfill_collect-date-month-id']
  recycle_prepare_list =  garbage_schedule['recycle_prepare-date-month-id']
  recycle_config = garbage_schedule['recycle_collect-date-month-id']
  compost_prepare_list = garbage_schedule['compost_prepare-date-month-id']
  compost_config = garbage_schedule['compost_collect-date-month-id']
  xmas_tree_config = garbage_schedule['holiday-tree-schedule_collect-date-month-id']


  #print("Checking garbage status...")

  dumpster = isgarbageday(today.strftime("%d%b"),dumpster_config)
  landfill = isgarbageday(today.strftime("%d%b"),landfill_config)
  recycle = isgarbageday(today.strftime("%d%b"),recycle_config)
  compost = isgarbageday(today.strftime("%d%b"),compost_config)
  xmas_tree = isgarbageday(today.strftime("%d%b"),xmas_tree_config)

  #print("Getting prepare times...")

  dumpster_prepapre = isgarbageday(today.strftime("%d%b"),dumpster_prepare_list)
  landfill_prepapre = isgarbageday(today.strftime("%d%b"),landfill_prepare_list)
  recycle_prepare = isgarbageday(today.strftime("%d%b"),recycle_prepare_list)
  compost_prepare = isgarbageday(today.strftime("%d%b"),compost_prepare_list)

  g_data = garbage_summary(landfill=landfill, recycle=recycle, compost=compost, xmas_tree=xmas_tree, landfill_prepapre=landfill_prepapre, recycle_prepare=recycle_prepare, compost_prepare=compost_prepare, dumpster=dumpster, dumpster_prepapre=dumpster_prepapre)
 
  #Fake Data generator below
  # g_data = garbage_summary(landfill=1, recycle=1, compost=1, xmas_tree=1, landfill_prepapre=0, recycle_prepare=0, compost_prepare=0, dumpster=1, dumpster_prepapre=0)
  # g_data = garbage_summary(landfill=0, recycle=0, compost=0, xmas_tree=0, landfill_prepapre=1, recycle_prepare=1, compost_prepare=1, dumpster=0, dumpster_prepapre=1)
  # g_data = garbage_summary(landfill=1, recycle=1, compost=1, xmas_tree=1, landfill_prepapre=1, recycle_prepare=1, compost_prepare=1, dumpster=1, dumpster_prepapre=1)

  return g_data
