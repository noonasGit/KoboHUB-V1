from datetime import date, time, datetime 
import time
import configparser

def get_transit_departures(file_path:str, schedule_key:str):
    parser = configparser.RawConfigParser()
    parser.read(file_path)
    data = []
    data = parser.get(schedule_key, "schedule")
    data = data.split(",")
    return data


def next_transit():
   # config from the file
   #Setup array of morning bus times for the week
   transit_weekly = get_transit_departures("generic_transit_schedules.ini","weekdays")
   transit_sat = get_transit_departures("generic_transit_schedules.ini","saturdays")
   transit_sun = get_transit_departures("generic_transit_schedules.ini","sundays")

   transit_check_schedule = []
   
   weekDay = datetime.now().strftime("%A")
   if weekDay == "Saturday" :
      transit_check_schedule = transit_sat
   if weekDay ==  "Sunday" :
      transit_check_schedule = transit_sun
   if weekDay != "Saturday" or weekDay != "Sunday" :
      transit_check_schedule = transit_weekly

   #Initiate the array

   buss_r = []
   if len(transit_check_schedule) > 0 :
       l = len(transit_check_schedule) - 1
   else :
      return []
   stop_time = transit_check_schedule[l]
   first_bus = transit_check_schedule[0]
   print("Loading departures for "+weekDay)
   print(str(len(transit_check_schedule))+" depatures loaded")
   print("First departure is at: "+first_bus)
   print("Last departure time is at: "+transit_check_schedule[l])
   start_time = datetime.now().strftime("%H:%M)")
   t = 0
   if start_time < stop_time or len(transit_check_schedule) == 0:
      print("No Transits to scan for...")
      return buss_r
   while t < len(transit_check_schedule):
      if start_time >= transit_check_schedule[t]:
         # print("Next ",t)
         t = t +1
         if (t+1) > len(transit_check_schedule):
            break
      if start_time < transit_check_schedule[t] :
         while t < len(transit_check_schedule) :
            #print("Adding departure "+transit_check_schedule[t].strftime("%H:%M"))
            buss_r.append(transit_check_schedule[t])
            t = t +1
   return buss_r
