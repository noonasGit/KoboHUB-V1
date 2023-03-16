# By Jonas Johansson
# This code extracts the stop times based on supplied stop_id using the API key.
# For the KoboHUB Dashboard

import requests
from requests.exceptions import RequestException
from datetime import datetime
import time
from json import loads

def gettransitdepartures(date_time:datetime, transit_apikey:str, stop_id:str):

    #MOCK DATA HERE
    mock_string = "{'route_departures': [{'global_route_id': 'STM:916', 'itineraries': [{'branch_code': '', 'direction_headsign': 'Est', 'direction_id': 0, 'headsign': 'Est', 'merged_headsign': 'Est', 'schedule_items': [{'departure_time': 1676524500, 'is_cancelled': False, 'is_real_time': False, 'rt_trip_id': '259680962', 'scheduled_departure_time': 1676524500, 'trip_search_key': 'STM:41355212:155:9:0', 'wheelchair_accessible': 0}, {'departure_time': 1676526240, 'is_cancelled': False, 'is_real_time': False, 'rt_trip_id': '259680408', 'scheduled_departure_time': 1676526240, 'trip_search_key': 'STM:41355212:155:9:1', 'wheelchair_accessible': 1}, {'departure_time': 1676544420, 'is_cancelled': False, 'is_real_time': False, 'rt_trip_id': '259680365', 'scheduled_departure_time': 1676544420, 'trip_search_key': 'STM:41355212:155:9:2', 'wheelchair_accessible': 1}]}], 'mode_name': 'Bus', 'real_time_route_id': '70', 'route_color': '174ba5', 'route_long_name': 'Bois-Franc', 'route_network_id': 'STM|Montréal', 'route_network_name': 'STM', 'route_short_name': '70', 'route_text_color': 'ffffff', 'route_type': 3, 'sorting_key': '70', 'tts_long_name': 'Bois-Franc', 'tts_short_name': '70'}]}"

    base_url = "https://external.transitapp.com/v3/public/stop_departures"
    apikey = "apikey="+transit_apikey
    global_stop = "global_stop_id="+stop_id
    bus_time = "time="+str(date_time.utcnow)
    remove_cancelled = "remove_cancelled=false"
    should_update_realtime = "should_update_realtime=true"
    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+global_stop+"&"+remove_cancelled+"&"+should_update_realtime
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    print("Connecting to Transit API...")
    headers = {
    'Accept-Language': "en"}
    for attempt in range(2):
        try:
            rawresponse = requests.get(url, params=headers)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("API call failed {}".format(e))
            time.sleep(2 ** attempt)
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    #print(rawresponse.ok)   
    
    if rawresponse.ok == True:
        return_data = []
        json_data = rawresponse.json()
        for i in json_data['route_departures'][0]['itineraries'][0]['schedule_items']:
            # print(i)
            return_data.append(i['departure_time'])
        return return_data
    else:
        print("Error gettin data from Transi API, "+rawresponse.reason)
        if rawresponse.reason == "Unauthorized" :
            print("API KEY ISSUE!!")
            print("Please ensure you have entered a correct API key for transit in the config.ini file")
            print("####################################################################################")
            print(api_error)
        return []


def get_stopid_by_lat_long(lat_value:str,lon_value:str,transit_apikey:str,max_dist:str):
    
    base_url = "https://external.transitapp.com/v3/public/nearby_stops"
    apikey = "apikey="+transit_apikey
    lat = "lat="+lat_value
    lon = "lon="+lon_value
    max_dist = "max_distance="+max_dist
    
    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+lat+"&"+lon+"&"+max_dist
    api_error = ""
    print("Connecting to Transit API...")
    headers = {
    'Accept-Language': "en"}
    for attempt in range(2):
        try:
            rawresponse = requests.get(url, params=headers)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("API call failed {}".format(e))
            time.sleep(2 ** attempt)
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    
    if rawresponse.ok == True:
        return_data = []
        json_data = rawresponse.json()
        for i in json_data['stops']:
            # print(i)
            return_data.append(str(i['global_stop_id'])+" local stop id -> "+str(i['rt_stop_id']))
        return return_data
    else:
        print("Error gettin data from Transi API, "+rawresponse.reason)
        if rawresponse.reason == "Unauthorized" :
            print("API KEY ISSUE!!")
            print("Please ensure you have entered a correct API key for transit in the config.ini file")
            print("####################################################################################")
            print(api_error)
        return []
