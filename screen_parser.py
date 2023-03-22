# By Jonas Johansson
# This tool will help you find the Transit API Global Stop ID used to configure the KoboHUB
# Created 2023
# For the KoboHUB Dashboard

from transit import gettransitdepartures, get_stopid_by_lat_long
import configparser
import os.path
from os import path
from datetime import date, datetime, timedelta

def get_screen_ref_data(file_path:str):
    if os.path.exists(file_path) :
        parser = configparser.RawConfigParser()
        parser.read(file_path)
        data = dict()
        data['times_id'] = parser.get("screen-refresh-schedule", "times")
        data['screen_rate_id'] = parser.get("screen-refresh-schedule", "screen_rate")
        data['backlit_setting_id'] = parser.get("screen-refresh-schedule", "backlit_setting")
        return data
    else :
        data = dict()
        data['times_id'] = "0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        data['screen_rate_id'] = "0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        data['backlit_setting_id'] = "0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        return data



# config from the file
cfg_file_data = get_screen_ref_data("koboHUB_refresh_schedule.ini")

times_data = cfg_file_data['times_id'].split(",")
screen_refresh_data = cfg_file_data['screen_rate_id'].split(",")
backlit_settings_data = cfg_file_data['backlit_setting_id'].split(",")


print(times_data,str(len(times_data)))
print(screen_refresh_data,str(len(screen_refresh_data)))
print(backlit_settings_data,str(len(backlit_settings_data)))

p = 0
while p < len(times_data):
    print("At "+str(times_data[p]+" - refresh rate is "+str(screen_refresh_data[p])+" and screen setting at "+str(backlit_settings_data[p])))
    p +=1

df = datetime.now() + timedelta(hours=6)
 

print("time is "+df.strftime("%H"))