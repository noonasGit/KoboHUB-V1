# By Jonas Johansson
# This tool will help you find the Transit API Global Stop ID used to configure the KoboHUB
# Created 2023
# For the KoboHUB Dashboard

from transit import gettransitdepartures, get_stopid_by_lat_long
import configparser
import os.path
from os import path

def get_config_data(file_path):
    print("Loading config data: "+file_path+"\n")
    if path.exists(file_path) :
        parser = configparser.RawConfigParser()
        parser.read(file_path)
        data = dict()
        data['transit-apikey_id'] = parser.get("koboHUB","transit-apikey")
    else :
        print("Open File failed, file "+file_path+" not found!\n\n")
        return ""
    return data

# config from the file
cfg_data = dict()
cfg_file_data = get_config_data("config.ini")
if len(cfg_file_data) > 0 :
    transit_apiKey = cfg_file_data['transit-apikey_id']
else :
    transit_apiKey = ""

print("Using API KEY: "+transit_apiKey+"\n")
print("This will help you get the value for the [transit-stop] when using the transit API\n")
skip = 0
while skip != 3 :
    if transit_apiKey == "" :
        transit_apiKey = input("Enter Transit API Key: ")
    lat_value = input("Enter latitude (e.g. 45.526168077787894): ")
    lon_value = input("Enter longitune (e.g. -73.59506067289408): ")
    max_dist =  input("Max radius (e.g. 150): ")
    if max_dist == "" :
        max_dist = "150"
        print("Radius set to 150 by default, you may need to incease this value if no stops are found\n")
        skip = 1
    if lat_value == "" :
        print ("You must enter the Latitude\n")
    else :
        skip = 2
    if lon_value == "" :
        print ("You must enter the Longitude\n")
    else:
        skip = 3
    
bus_stop_id = []
bus_stop_id = get_stopid_by_lat_long(lat_value,lon_value,transit_apiKey,max_dist)

print("Getting stop ID's for location..\n\n")
if len(bus_stop_id) == 0:
    print("No stops goten, increase the Max radius and try again\n\n")
else:
    print("Found "+str(len(bus_stop_id))+" stops\n")
    print("Global_stop_id  ->  local stop id ")
    print("_________________________________\n")
    for i in bus_stop_id :
        print(i)
    print("\n")
    print("Take the the id starting with XXX:NNNNN and map it to the one printed on your local stop\n")
    print("Example in Long Island NICE:46145 local stop id 3847")
    print("The NICE:46145 is the transit ID, mapped to a Local stop id 3847 - this is usually printed on the stop sign")
    print("Enter the XXXX:####into the config.ini")
    print("Example: transit-stop=NICE:46145\n\n")




