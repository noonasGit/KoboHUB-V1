from cgitb import small
import configparser
from dataclasses import dataclass
from operator import ne
from typing import List
import socket
import tempfile
import time
from datetime import datetime, date, timedelta
from subprocess import call
from sys import platform
import os
from xml.etree.ElementInclude import include

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from PIL.Image import Image as PilImage
from weather import weather_current, weather_forecast, koboHUBWeather

from garbage_schedule import get_garbage_status, get_garbage_config_data
from getcomic import getComicFile
from generic_transit import next_transit
from transit import gettransitdepartures
from getquote import quoteoftheday

try:
    from _fbink import ffi, lib as fbink
except ImportError:
    from fbink_mock import ffi, lib as fbink

CONFIGFILE = "config.ini"
#Preset of global variable
kobo_blight = 0
os.system("fbink -q --clear --flash")

def wait_for_wifi():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
            return ip_addr
        except Exception as e:
            print("exc. ignored {}".format(e))
            os.system("reboot")
        time.sleep(15)

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
        data['screen_rate_id'] = "60,60,60,60,65,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60"
        data['backlit_setting_id'] = "0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        return data


def get_config_data(file_path:str, show_icons:int):
    screen_orientation = get_screen_orientation()
    """turns the config file data into a dictionary"""
    parser = configparser.RawConfigParser()
    parser.read(file_path)
    data = dict()
    data['ow-api-key_id'] = parser.get("koboHUB", "ow-api-key")
    data['ow-city_id'] = parser.get("koboHUB", "ow-city")
    data['ow-units_id'] = parser.get("koboHUB", "ow-units")
    data['ow-language_id'] = parser.get("koboHUB","ow-language")
    data['show-comic_id'] = parser.get("koboHUB","show-comic")
    data['comic_id'] = parser.get("koboHUB", "comic")
    data['comic_morning_id'] = parser.get("koboHUB", "comic-morning")
    data['comic_midday_id'] = parser.get("koboHUB", "comic-midday")
    data['comic_afternoon_id'] = parser.get("koboHUB", "comic-afternoon")
    data['comic_evening_id'] = parser.get("koboHUB", "comic-evening")
    data['transit-feature_id'] = parser.get("koboHUB","transit-feature")
    data['transit-icon_id'] = parser.get("koboHUB","transit-icon")
    data['transit-id_id'] = parser.get("koboHUB","transit-id")
    data['transit-stop-name_id'] = parser.get("koboHUB","transit-stop-name")
    data['use-transit-api_id'] = parser.get("koboHUB","use-transit-api")
    data['transit-apikey_id'] = parser.get("koboHUB","transit-apikey")
    data['transit-stop_id'] = parser.get("koboHUB","transit-stop")
    data['use-generic-transit_id'] = parser.get("koboHUB","use-generic-transit")
    data['generic-transit-timeframe_id'] = parser.get("koboHUB","generic-transit-timeframe")
    data['live-cutin-time-start_id'] = parser.get("koboHUB","live-cutin-time-start")
    data['live-cutin-time-stop_id'] = parser.get("koboHUB","live-cutin-time-stop")
    data['quote-of-the-day-show_id'] = parser.get("koboHUB","quote-of-the-day-show")
    data['quote-of-the-day-max-lenght_id'] = parser.get("koboHUB","quote-of-the-day-max-lenght")
    data['screen-orientation_id'] = parser.get("koboHUB","screen-orientation")
    data['garbage-show_id'] = parser.get("koboHUB","garbage-show")
    data['koboHUB-refresh-seconds_id'] = parser.get("koboHUB","koboHUB-refresh-seconds")
    data['koboHUB-var-refresh_id'] = parser.get("beta","koboHUB-var-refresh")
    data['koboHUB-backlight_id'] = parser.get("koboHUB","koboHUB-backlight")

    if show_icons == 1:
        if screen_orientation == "LANDSCAPE" :
            config_x = 20
        else :
            config_x = 10
        config_y = 10
        image_file = 'icons/loading_icons_openweather.png'
        if data['ow-units_id'] == "metric":
            image_file = 'icons/loading_icons_openweather_metric.png'
        if data['ow-units_id'] == "imperial":
            image_file = 'icons/loading_icons_openweather_imperial.png'
        os_cmd ="fbink -q --image file="+image_file+",x="+str(config_x)+",y="+str(config_y)+" > /dev/null"  
        os.system(os_cmd)
        config_x = config_x + 84
        if data['show-comic_id'] == "TRUE":
            image_file = 'icons/loading_icons_gocomics.png'
            os_cmd ="fbink -q --image file="+image_file+",x="+str(config_x)+",y="+str(config_y)+" > /dev/null"  
            os.system(os_cmd)
            config_x = config_x + 84
            time.sleep(1)
        if data['transit-feature_id'] == "TRUE":
            image_file = 'icons/loading_icons_transit.png'
            os_cmd ="fbink -q --image file="+image_file+",x="+str(config_x)+",y="+str(config_y)+" > /dev/null"  
            os.system(os_cmd)
            config_x = config_x + 84
            time.sleep(1)
        if data['use-transit-api_id'] == "TRUE":
            image_file = 'icons/loading_icons_transit_app.png'
            os_cmd ="fbink -q --image file="+image_file+",x="+str(config_x)+",y="+str(config_y)+" > /dev/null"  
            os.system(os_cmd)
            config_x = config_x + 84
            time.sleep(1)
        if data['garbage-show_id'] == "TRUE" :
            image_file = 'icons/loading_icons_trash.png'
            os_cmd ="fbink -q --image file="+image_file+",x="+str(config_x)+",y="+str(config_y)+" > /dev/null"  
            os.system(os_cmd)
            config_x = config_x + 84
            time.sleep(1)
    return data

@dataclass
class box_descriptor:
    pos_x: int
    pos_y: int
    width: int
    height: int

@dataclass
class boxes:
    current: box_descriptor
    today: box_descriptor
    tomorrow: box_descriptor
    next_days: List[box_descriptor]


@dataclass
class fonts:
    micro: FreeTypeFont
    tiny: FreeTypeFont
    small: FreeTypeFont
    medium: FreeTypeFont
    quote: FreeTypeFont
    weather_stats: FreeTypeFont
    weather_stats_bold: FreeTypeFont
    comfort_small: FreeTypeFont
    comfort: FreeTypeFont
    comfortB: FreeTypeFont
    comfortBH: FreeTypeFont
    larger : FreeTypeFont
    SFCompact_tiny : FreeTypeFont
    SFCompact_tinyB : FreeTypeFont
    SFCompact : FreeTypeFont
    SFCompact_Big : FreeTypeFont
    bus_times_font : FreeTypeFont


@dataclass
class icons:
    wind: PilImage
    humidity: PilImage
    temperature: PilImage

@dataclass
class data:
    current: weather_current
    forecast: List[weather_forecast]

@dataclass
class garbage_summary:
    landfill: bool
    recycle: bool
    xmas_tree: bool
    landfill_prepapre : bool
    recycle_prepare : bool
    dumpster : bool
    dumpster_prepapre : bool


class koboHUB:
    # BORDER, in pixels, so we don't draw too close to the edges
    BORDER = 10
    def __init__(self):

        # config from the file
        self.cfg_data = dict()
        cfg_file_data = get_config_data(CONFIGFILE,0)
        self.cfg_data['ow-api-key'] = cfg_file_data['ow-api-key_id']
        self.cfg_data['ow-city'] = cfg_file_data['ow-city_id']
        self.cfg_data['ow-units'] = cfg_file_data['ow-units_id']
        self.cfg_data['ow-language'] = cfg_file_data['ow-language_id']
        self.cfg_data['show-comic'] = cfg_file_data['show-comic_id']
        self.cfg_data['comic'] = cfg_file_data['comic_id']
        self.cfg_data['comic-morning'] = cfg_file_data['comic_morning_id']
        self.cfg_data['comic-midday'] = cfg_file_data['comic_midday_id']
        self.cfg_data['comic-afternoon'] = cfg_file_data['comic_afternoon_id']
        self.cfg_data['comic-evening'] = cfg_file_data['comic_evening_id']
        self.cfg_data['transit-feature'] = cfg_file_data['transit-feature_id']
        self.cfg_data['transit-icon'] = cfg_file_data['transit-icon_id']
        self.cfg_data['transit-id'] = cfg_file_data['transit-id_id']
        self.cfg_data['transit-stop-name'] = cfg_file_data['transit-stop-name_id']
        self.cfg_data['use-transit-api'] = cfg_file_data['use-transit-api_id']
        self.cfg_data['transit-apikey'] = cfg_file_data['transit-apikey_id']
        self.cfg_data['transit-stop'] = cfg_file_data['transit-stop_id']
        self.cfg_data['use-generic-transit'] = cfg_file_data['use-generic-transit_id']
        self.cfg_data['generic-transit-timeframe'] = cfg_file_data['generic-transit-timeframe_id']
        self.cfg_data['live-cutin-time-start'] = cfg_file_data['live-cutin-time-start_id']
        self.cfg_data['live-cutin-time-stop'] = cfg_file_data['live-cutin-time-stop_id']
        self.cfg_data['quote-of-the-day-show'] = cfg_file_data['quote-of-the-day-show_id']
        self.cfg_data['quote-of-the-day-max-lenght'] = cfg_file_data['quote-of-the-day-max-lenght_id']
        self.cfg_data['screen-orientation'] = cfg_file_data['screen-orientation_id']
        self.cfg_data['garbage_schedule'] = cfg_file_data['garbage-show_id']
        self.cfg_data['koboHUB-backlight'] = cfg_file_data['koboHUB-backlight_id']
        cfg_file_data = get_screen_ref_data("koboHUB_refresh_schedule.ini")

        self.times_data = cfg_file_data['times_id'].split(",")
        self.screen_refresh_data = cfg_file_data['screen_rate_id'].split(",")
        self.backlit_settings_data = cfg_file_data['backlit_setting_id'].split(",")

        # fbink configuration
        self.fbink_cfg = ffi.new("FBInkConfig *")
        self.fbink_cfg.is_centered = True
        self.fbink_cfg.is_halfway = True
        self.fbink_cfg.is_cleared = True

        self.fbfd = fbink.fbink_open()
        fbink.fbink_init(self.fbfd, self.fbink_cfg)
        state = ffi.new("FBInkState *")
        fbink.fbink_get_state(self.fbink_cfg, state)

        if "linux" in platform:
            self.screen_size = get_kobo_screen_size()
            self.screen_size = (state.view_width, state.view_height)
        else:
            self.screen_size = (768, 1024)

        # app configuration
        self.ip_address = "1.1.1.1"

        # weather class instance
        try:
            self.weather_fetcher = koboHUBWeather(self.cfg_data)
            self.weather = data(current=self.weather_fetcher.get_weather_current(),
                                forecast=self.weather_fetcher.get_weather_forecast())
        except Exception as e:
            print("Weather: Error getting weather")
            print(e)
            fbink.fbink_close(self.fbfd)

        # configuration for the image
        # Boxes positions
        #   current condition
        current = box_descriptor(0, 0, int(self.screen_size[0]), 350)
        #   today's forecast
        today = box_descriptor(current.width, 0, self.screen_size[0] - current.width, current.height)
        #   tomorrow
        tomorrow = box_descriptor(0, current.height, int( self.screen_size[0]) , 200)
        #   next 3 days
        next_day0 = box_descriptor(0, ( current.height + tomorrow.height ), int(self.screen_size[0]), int( self.screen_size[1] - current.height - tomorrow.height))
        next_day1 = box_descriptor(next_day0.width, next_day0.pos_y, next_day0.width, next_day0.height)
        next_day2 = box_descriptor(next_day1.pos_x + next_day1.width, next_day1.pos_y, next_day1.width, next_day1.height)
        self.boxes = boxes(current, today, tomorrow, [next_day0, next_day1, next_day2])
        # fonts
        #   tiny: used on the weather condition for the next days and ip address
        #   small: used on the headers and most stuff on the current conditions
        #   comfort: temperatures (gets scaled according to the box)
        #   big: for the current temperature
        self.fonts = fonts(micro=ImageFont.truetype("fonts/Fabrica.otf", 16),
                           tiny=ImageFont.truetype("fonts/segoe-ui.ttf", 22),
                           small=ImageFont.truetype("fonts/Fabrica.otf", 26),
                           weather_stats=ImageFont.truetype("fonts/SF-Compact-Rounded-Regular.ttf", 26),
                           weather_stats_bold=ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", 26),
                           medium=ImageFont.truetype("fonts/SF-Compact-Rounded-Regular.ttf", int(self.screen_size[0] / 22)),
                           quote=ImageFont.truetype("fonts/SF-Compact-Text-ThinItalic.ttf",int(self.screen_size[0] / 22) ),
                           comfort=ImageFont.truetype("fonts/Comfortaa-Regular.ttf", int(self.screen_size[0] / 8)),
                           comfort_small=ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", int(self.screen_size[0] / 18)),
                           comfortBH=ImageFont.truetype("fonts/Mont-Heavy-Bold.otf", int(self.screen_size[0] / 10)),
                           comfortB=ImageFont.truetype("fonts/Comfortaa-Bold.ttf", int(self.screen_size[0] /14)),
                           SFCompact_tiny=ImageFont.truetype("fonts/SF-Compact-Rounded-Regular.ttf", int(self.screen_size[0] / 26)),
                           SFCompact_tinyB=ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", int(self.screen_size[0] / 26)),
                           SFCompact=ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", int(self.screen_size[0] / 28)),
                           SFCompact_Big=ImageFont.truetype("fonts/SF-Compact-Rounded-Bold.ttf", int(self.screen_size[0] / 8)),
                           bus_times_font=ImageFont.truetype("fonts/RobotoMono-Bold.ttf", int(self.screen_size[0] / 22) ),
                           larger=ImageFont.truetype("fonts/segoe-ui.ttf", int(self.screen_size[0] / 20)))
        self.daycount = datetime.now().strftime("%d")
        self.daycount = "0"

        # icons
        self.icons = icons(wind=Image.open('icons/w.png'),
                           humidity=Image.open('icons/h.png'),
                           temperature=Image.open('icons/C.png'))

       
    def _create_image(self) -> str:
        global HOURGLASS, gTy, quote
        screen_rotation = get_screen_orientation()
        today = self.weather.forecast[0]
        tomorrow = self.weather.forecast[1]
        days = self.weather.forecast[2:]
        currenttime = datetime.now()
        X_OFFSET = 0
        if screen_rotation == "LANDSCAPE" :
            X_OFFSET = 10
            #Pushing the screen slightly to the right as rotation has a left shift it seems


        print("KoboHUB: Preparing dashboard image . . .")

        # 758 x 1024
        WIDTH = int(self.screen_size[0])
        HEIGHT = int(self.screen_size[1])

        white = 255
        black = 0
        gray = 132

        img = Image.new('L', (WIDTH, HEIGHT), color=white)
        draw = ImageDraw.Draw(img, 'L')

        # Find out how many characters per line of screen for garbage text
        test_t = "H"
        test_w_max = int(self.screen_size[0] - 200)
        text_c = 0
        test_t_w = 10
        while test_t_w < test_w_max :
            test_t = test_t + "H"
            test_t_w, test_t_h = draw.textsize(test_t, font=self.fonts.medium)
            #print("Quote Feature : Max text width is "+str(test_t_w)+" number of chars "+str(len(test_t)))
        self.max_chars = test_t_w

       # Find out how many characters per line of screen for Quotes
        test_t = "H"
        test_w_max = int(self.screen_size[0] - 200)
        text_c = 0
        test_t_w = 0
        while test_t_w < test_w_max :
            test_t = test_t + "H"
            test_t_w, test_t_h = draw.textsize(test_t, font=self.fonts.quote)
            #print("Quote Feature : Max text width is "+str(test_t_w)+" number of chars "+str(len(test_t)))
        self.max_charsQ = test_t_w
        # Dividing lines
        # under today/current
        draw.line([(self.BORDER, self.boxes.current.height), (WIDTH - self.BORDER, self.boxes.current.height)], gray)
        # between today/current | DISABLED
        # draw.line([(self.boxes.current.width, self.BORDER), (self.boxes.current.width, self.boxes.current.height - self.BORDER)], gray)
        # under tomorrow
        # draw.line([(self.BORDER, self.boxes.next_days[0].pos_y), (WIDTH - self.BORDER, self.boxes.next_days[0].pos_y)], gray)
        #Below comic line
        # draw.line([(self.BORDER, self.boxes.next_days[1].pos_y), (WIDTH - self.BORDER, self.boxes.next_days[1].pos_y)], gray)
        
        # Decide if we want to draw more lines for weather or leave it for Garbage area.

        # Current conditions
        # City Name, Country Code, Day, Time
        header_Day = datetime.now().strftime("%A")
        header_Month_Date = datetime.now().strftime("%b %-d")
        header_w, header_h = draw.textsize(header_Day, font=self.fonts.comfortBH)
        header_w2, header_h2 = draw.textsize(header_Month_Date, font=self.fonts.comfortB)

        # Show Day big letters and Month date ontop Banner
        # Draw day big letters in gray
        x = 10 + X_OFFSET
        y = 10
        draw.text((x, y), header_Day, font=self.fonts.comfortBH, fill=gray)
     
        # Draw Month and date Black on top
        xoff = X_OFFSET + ( int(header_w2) / 2)
        x = int(header_w) - xoff
        y = (int(header_h) / 2) + 10
        draw.text((x, y), header_Month_Date, font=self.fonts.comfortB, fill=black)

        # Current condition mini icon
        condition = Image.open(self.weather.current.icon)
        condition = condition.resize((int(condition.size[0] /1.2), int(condition.size[1] / 1.2)))
        x_icon_mini = int (x + header_w2) + 5
        y_icon_mini = 15
        img.paste(condition, (x_icon_mini,y_icon_mini))

        #Transit schedule#

         ###########
        #############
        ##   BUS   ##
        ##         ##
        #############
        ###       ###
        
        if self.cfg_data['transit-feature'] == "TRUE" :
            transit_icon_file = "Icons/buss_80x80.png"
            if self.cfg_data['transit-icon'] =="BUS":
                transit_icon_file = "Icons/buss_80x80.png"
            if self.cfg_data['transit-icon'] =="METRO":
                transit_icon_file = "Icons/metro_80x80.png"
            if self.cfg_data['transit-icon'] =="TRAM":
                transit_icon_file = "Icons/tram_80x80.png"

            transit_icon = Image.open(transit_icon_file)
            bx = self.screen_size[0] - (transit_icon.size[0] + 50)
            by = 70
            # blx = bx + ( int(transit_icon.size[0]) - int(bus_live_icon.size[0]/2)) + 5
            # bly = by - (int(bus_live_icon.size[1]/2))
            img.paste(transit_icon,(bx,by))
            x = bx + 20
            y = by + 3
            bus_t_w, bus_t_h = draw.textsize(self.cfg_data['transit-id'], font=self.fonts.larger)
            x = bx + ( int(transit_icon.size[0]/2) - int(bus_t_w/2) )
            draw.text((x, y), self.cfg_data['transit-id'], font=self.fonts.larger, fill=black)

            stop_t_w, stop_t_h = draw.textsize(self.cfg_data['transit-stop-name'], font=self.fonts.micro)
            x = (bx + int((transit_icon.size[0]/2)) ) - int( (stop_t_w/2) )
            y = by + int( transit_icon.size[1] + 4 )
            draw.text((x, y), self.cfg_data['transit-stop-name'], font=self.fonts.micro, fill=black)

            # LIVE Bus Schedule
            bus_times = []
            get_live_bus_times = []

            #Decide here to call the STM API - maybe only mon-fry and 6 to 11?
            
            if self.cfg_data['use-transit-api'] == "TRUE":
                print("Transit API :Feature ON")
                if currenttime > currenttime.replace(hour=int(self.cfg_data['live-cutin-time-start']), minute=0) and currenttime <= currenttime.replace(hour=int(self.cfg_data['live-cutin-time-stop']), minute=0) or self.cfg_data['generic-transit-timeframe'] == "FALSE":
                    print("Transit API :Getting LIVE transit times...")
                    bus_time_status_icon = Image.open("icons/live24x24.png")
                    get_live_bus_times = gettransitdepartures(datetime.now(),self.cfg_data['transit-apikey'],self.cfg_data['transit-stop'])
                    if len(get_live_bus_times) == 0:
                        print("Transit API :Error getting live times...")
                    else:
                        #Convert the datetime to HH:MM array here.
                        for i in get_live_bus_times :
                            bus_times.append(datetime.fromtimestamp(i).strftime('%H:%M'))
                if self.cfg_data['use-generic-transit'] == "TRUE" and len(get_live_bus_times) == 0:
                    #Time Table - Hard coded in generic_transit.py - returned as HH:MM arrays no conversion needed.
                    print("Transit (Static) :Using static transit time table data")
                    bus_time_status_icon = Image.open("icons/not_live24x24.png")
                    bus_times = next_transit()

                b = len(bus_times)
                if len(get_live_bus_times) :
                    print("Transit Feature :"+str(len(get_live_bus_times))+" Live times found")
                else:
                    print("Transit Feature :"+str(b)+" Bus schedules found")
                bc = 0
                bus_w, bus_h = draw.textsize("00:00", font=self.fonts.bus_times_font)
                x = (bx + int((transit_icon.size[0]/2)) ) - int( (bus_w/2) )
                y = y + 10
                blx = x + (int(bus_w)+ 5)
                bly = y + 6

                if b > 0 :
                    while bc < 3 :
                        draw.text((x, y), bus_times[bc], font=self.fonts.bus_times_font, fill=black)
                        img.paste(bus_time_status_icon,(blx,bly))
                        bc = bc +1
                        y = y + (bus_h)
                        bly = bly + bus_h 
                if b == 0 :
                    draw.text((x, y), "--:--", font=self.fonts.bus_times_font, fill=black)
        else:
            print("Transit Feature :OFF")

            ###
        ###     ###
        ###     
        ### 
        ###     ###
            ###

        
        # Draw actual like temp middle of screen large
        temp_w, temp_h = draw.textsize(str(round(self.weather.current.temperature,1 ))+"\N{DEGREE SIGN}", font=self.fonts.SFCompact_Big) 
        x = (self.screen_size[0]/2)-(temp_w/2)
        y = 120
        draw.text((x, y), str(round(self.weather.current.temperature, 1))+"\N{DEGREE SIGN}", font=self.fonts.SFCompact_Big, fill=black)


        # condition description - under the current temp
        cond_w, cond_h = draw.textsize(self.weather.current.condition.capitalize(), font=self.fonts.larger) 
        x = (self.screen_size[0]/2)-(cond_w/2) 
        y = y + (temp_h + 10)
        draw.text((x, y), self.weather.current.condition.capitalize(), font=self.fonts.larger, fill=black)

        # Combined H / L
        today_cond_combined_temp = "H: "+str(round(today.high,1))+"\N{DEGREE SIGN}"+" L: "+str(round(today.low,1))+"\N{DEGREE SIGN}"
        condition_w, condition_h = draw.textsize(today_cond_combined_temp, font=self.fonts.SFCompact)
        x = (self.screen_size[0]/2)-(condition_w/2)
        y = y + (cond_h + 10)
        draw.text((x, y), today_cond_combined_temp, font=self.fonts.SFCompact, fill=gray)

        ###  METRICS TO THE LEFT
        
        #Set X Y for site weather stats
        
        x = 20 + X_OFFSET
        y = 100
        
        # Thermometer
        weather_font = self.fonts.weather_stats
        thermometer_icon = Image.open("Icons/t.png")
        if self.weather.current.feelslike <= -5:
           thermometer_icon = Image.open("Icons/temp_low.png")
           weather_font =  self.fonts.weather_stats_bold
        if self.weather.current.feelslike > -1 and self.weather.current.temperature < 20:
           thermometer_icon = Image.open("Icons/t.png")
        if self.weather.current.feelslike >= 21 :
           thermometer_icon = Image.open("Icons/temp_high.png")
           weather_font =  self.fonts.weather_stats_bold

        # Draw  feels like temp next to icon
        img.paste(thermometer_icon,(x,y))
        xt = x + thermometer_icon.size[0] + 5
        yt = y -4
        draw.text((xt, yt), "Feels like", font=weather_font, fill=gray)
        yt = yt + 24
        draw.text((xt, yt), str(round(self.weather.current.feelslike, 1))+"\N{DEGREE SIGN}", font=weather_font, fill=black)
        '''

        # Draw  feels like temp next to icon
        img.paste(thermometer_icon,(x,y))
        xt = x + thermometer_icon.size[0] + 5
        yt = y + 10
        draw.text((xt, yt), str(round(self.weather.current.feelslike, 1))+"\N{DEGREE SIGN}", font=weather_font, fill=black)

        '''
        
        # Step down for next values
        y = y + 50

        # pressure icon
        weather_font = self.fonts.weather_stats
        if self.weather.current.pressure <= 990 :
           pressure_icon = Image.open("icons/p_low.png")
           weather_font =  self.fonts.weather_stats_bold
           weather_pressure_text = "Low"
        if self.weather.current.pressure > 990 and self.weather.current.pressure <= 1025:
           pressure_icon = Image.open("icons/p.png")
           weather_pressure_text = "Normal"
        if self.weather.current.pressure > 1025 :
           pressure_icon = Image.open("icons/p_high.png")
           weather_font =  self.fonts.weather_stats_bold
           weather_pressure_text = "High"
        # Draw icon and text
        img.paste(pressure_icon, (x, y))
        xt = x + pressure_icon.size[0] + 5
        yt = y + 10
        draw.text((xt, yt), weather_pressure_text, font=weather_font, fill=black)

        # Step down for next values
        y = y + 50

        # humidity icon
        weather_font = self.fonts.weather_stats
        if int(round(self.weather.current.humidity, 0)) <= 45 :
           humid_icon = Image.open("icons/h_low.png")
        if int(round(self.weather.current.humidity, 0)) > 45 and int(round(self.weather.current.humidity, 0)) <= 80 :
           humid_icon = Image.open("icons/h.png")
        if int(round(self.weather.current.humidity, 0)) > 80 :
           humid_icon = Image.open("icons/h_high.png")
           weather_font = self.fonts.weather_stats

        img.paste(humid_icon, (x, y))
        xt = x + humid_icon.size[0] + 5
        yt = y + 10

        # humidity value
        humidity_w, humidity_h = draw.textsize(str(int(round(self.weather.current.humidity, 0))) + "%", font=weather_font)
        draw.text((xt, yt), str(int(round(self.weather.current.humidity, 0))) + "%", font=weather_font, fill=black)

        # Step down for next values
        y = y + 50

        # Wind icon
        weather_font = self.fonts.weather_stats
        if round(self.weather.current.wind, 0) <= 30 :
            wind_icon = Image.open("icons/w_low.png")
        if round(self.weather.current.wind) > 30 and round(self.weather.current.wind) <= 50 :
            wind_icon = Image.open("icons/w.png")
        if round(self.weather.current.wind) > 50 :
            wind_icon = Image.open("icons/w_high.png")
            weather_font =  self.fonts.weather_stats_bold

        img.paste(wind_icon, (x, y))

        # wind value
        xt = x + wind_icon.size[0] + 5
        yt = y + 10
        wind_w, wind_h = draw.textsize(str(int(round(self.weather.current.wind, 0))) + "km/h", font=weather_font)
        draw.text((xt, yt), str(int(round(self.weather.current.wind, 0))) + "km/h", font=weather_font, fill=black)

        


        # TOMORROW's forecast MINI
        # tomorrow's text
        # Current conditions
        
        Tomorrow_Days = datetime.now() + timedelta(days=1)
        Tomorrow_Day = Tomorrow_Days.strftime("%A :")
        header_w, header_h = draw.textsize(Tomorrow_Day, font=self.fonts.SFCompact_tinyB)
        x = 20 + X_OFFSET
        y = self.boxes.today.height - int(header_h +14)
        draw.text((x,y),Tomorrow_Day,font=self.fonts.SFCompact_tinyB, fill=black)
            
        

        # Draw the condition icon mini
        condition = Image.open(tomorrow.icon)
        condition = condition.resize((int(condition.size[0] /3), int(condition.size[1] / 3)))
        x = x + int(header_w +4)
        iy = y 
        img.paste(condition, (x, iy))

     
        # Print Tomorrows forecast
        xoff = x + int( condition.size[0]+4 )

        condition_w, condition_h = draw.textsize(tomorrow.condition.capitalize(), font=self.fonts.SFCompact_tiny)
        tomorrow_cond_trunc = tomorrow.condition.capitalize()[0:16]
        tomorrow_summary = tomorrow_cond_trunc+" | H: "+str(round(tomorrow.high,1))+"\N{DEGREE SIGN}"+" L: "+str(round(tomorrow.low,1))+"\N{DEGREE SIGN}" 
        draw.text((xoff, y), tomorrow_summary, font=self.fonts.SFCompact_tiny, fill=black)
        
        y_offset = 0
        # COMIC Pane drawing
        if self.cfg_data['show-comic'] == "TRUE" :
            comicfile = "comics/404.jpg"            
            comictitle = "none"
            if currenttime >= currenttime.replace(hour=5, minute=0) and currenttime <= currenttime.replace(hour=9, minute=0) :
                comictitle = self.cfg_data['comic-morning']
                #print("Morning Comic is: "+comictitle)
            if currenttime > currenttime.replace(hour=9, minute=0) and currenttime <= currenttime.replace(hour=11, minute=0) :
                comictitle = self.cfg_data['comic-midday']
                #print("Midday Comic is: "+comictitle)
            if currenttime > currenttime.replace(hour=11, minute=0) and currenttime <= currenttime.replace(hour=17, minute=0) :
                comictitle = self.cfg_data['comic-afternoon']
                #print("Afternoon Comic is: "+comictitle)
            if currenttime > currenttime.replace(hour=17, minute=0) and currenttime <= currenttime.replace(hour=23, minute=0) :
                comictitle = self.cfg_data['comic-evening']
                #print("Evening Comic is: "+comictitle)
            if currenttime > currenttime.replace(hour=0, minute=0) and currenttime <= currenttime.replace(hour=4, minute=0) :
                comictitle = self.cfg_data['comic-evening']
                #print("Evening Comic is: "+comictitle)

            print("Comic Feature : Comis is "+comictitle)
            get_comicdata = getComicFile(comictitle)
            comicfile = get_comicdata.comic_url
            comictitle = get_comicdata.comic_title

            if comicfile == "Nofile" :
                comicfile = "comics/404.jpg"
        
            print("Comic is: ",comicfile)
            if comicfile != "Nofile" :
                comic_image = Image.open(comicfile)
                print("Comic Feature : Comic Strip is "+str(comic_image.size[0])+" by "+str(comic_image.size[1]))
                print("Comic Feature : Screen size is "+str(self.screen_size[0])+" by "+str(self.screen_size[1]))
                if comic_image.size[0] > self.screen_size[0]:
                    comic_scale_factor = (self.screen_size[0] - 10) / comic_image.size[0]
                    print("Comic Feature : Scaling the comic down to "+str(comic_scale_factor))
                    comic_image = comic_image.resize((int(comic_image.size[0] * comic_scale_factor), int(comic_image.size[1] * comic_scale_factor)))
                    print("Comic Feature : Comic size is now "+str(comic_image.size[0])+" by "+str(comic_image.size[1]))
                elif comic_image.size[0] < self.screen_size[0]:
                    comic_scale_factor = comic_image.size[0] / (self.screen_size[0] - 10)
                    print("Comic Feature : Scaling the comic up to "+str(comic_scale_factor))
                    comic_image = comic_image.resize((int(comic_image.size[0] / comic_scale_factor), int(comic_image.size[1] / comic_scale_factor)))
                    print("Comic Feature : Comic size is now "+str(comic_image.size[0])+" by "+str(comic_image.size[1]))
            if comicfile != "Nofile" :
                Cx = int((self.screen_size[0]/2)) - int((comic_image.size[0])/2) + X_OFFSET
                Cy = int(self.boxes.tomorrow.pos_y)
                img.paste(comic_image,(Cx,Cy))
                y_offset = Cy + int(comic_image.size[1])
                #print("Setting Y offset to "+str(y_offset))
        else:
            print("Comic Feature : OFF")
        
        #########################
        #Quote of the day section
        #########################
        if self.cfg_data['quote-of-the-day-show'] == "TRUE" :
                qml = int(self.cfg_data['quote-of-the-day-max-lenght'])
                qll = qml+1
                qmaxtries = 0
                if int( currenttime.strftime("%d") ) > int( self.daycount ):
                    self.daycount = datetime.now().strftime("%d")
                    print("Quote Feature : Getting a quote under "+str(qml)+" lenght")
                    while qll >= qml :
                        quote = quoteoftheday()
                        qll = len(quote.quote_text)
                        qmaxtries +=1
                        if qmaxtries > 10:
                            break
                        if qll > qml:
                            print("Quote Feature : Attempt: "+str(qmaxtries))
                        else:
                            print("Quote Feature : Quote lenght is "+str(qll))

                    if qll > qml:
                        print("Quote Feature : Max attempts to get a short enough quote exhausted.")
                        #Just in case we could not find a short enough quote in 10 attempts.
                        quote.quote_text = "Sorry, No short Quote found, please adjust the quote-of-the-day-max-lenght value"
                        quote.quote_author = "KoboHUB"
                    print("Quote Feature : "+quote.quote_text+" - "+quote.quote_author)
                else:
                    next_quote_hour = datetime.now() + timedelta(days=1)
                    print("Quote Feature : Keeping quote, next one at "+next_quote_hour.strftime("%d")+" daycount at "+str(self.daycount))              
                #print("Now trying to slice the text in chunks")
                test_t_w, test_t_h = draw.textsize(quote.quote_text, font=self.fonts.quote)
                text_max = test_t_w
                text_line_max = self.max_charsQ
                
                text_line = []
                textbuffer = ""
                #Split the quote into words in an array
                quote_words = quote.quote_text.split()
                wl = len(quote.quote_text)
                #See if the total is larger than the text_line_max value set.
                if text_max > text_line_max:
                    l = 0
                    ql = len(quote_words)
                    while l < ql:
                        textbuffer = textbuffer + quote_words[l] + " "
                        l += 1
                        test_t_w, test_t_h = draw.textsize(textbuffer, font=self.fonts.quote)
                        #print(textbuffer)
                        if test_t_w > text_line_max:
                            text_line.append(textbuffer)
                            textbuffer = ""
                        #print(l)
                    if (len(textbuffer)):
                        text_line.append(textbuffer)    
                else :
                    text_line.append(quote.quote_text)

                # Get number of arrays generated    
                qs = len(text_line)
                qc = 0
                qx = 20 + X_OFFSET
                g_w = 0
                q_h = 0
                q_w = 0

                #Getting the widest line of text
                tq_w, tq_h = draw.textsize(text_line[qc], font=self.fonts.medium)
                while qc < qs :
                    tq_w, tq_h = draw.textsize(text_line[qc], font=self.fonts.medium)
                    q_h = tq_h
                    if tq_w > q_w :
                        q_w = tq_w
                    qc +=1

                #Writing the quote line by line.
                qc = 0

                gTx = 10 + X_OFFSET
                # gTy = self.screen_size[1] - 280
                if y_offset == 0 :
                    gTy = int(self.boxes.tomorrow.pos_y + 5) + y_offset
                else:
                    gTy = y_offset


                if self.cfg_data['show-comic'] == "TRUE" :
                    draw.line([(0, gTy), (WIDTH, gTy)], gray)
                    print("Quote Feature : Drawing a line to separate")
                    gTy = gTy + 5

                # Show the Quote Icon
                quote_icon = Image.open("icons/quote_icon.png")
                img.paste(quote_icon,(gTx, gTy))
                gTx = gTx + int(quote_icon.size[0]+4)


                while qc < qs:
                    draw.text((gTx, gTy), text_line[qc], font=self.fonts.quote, fill=black)
                    #print(text_line[qc])
                    qc += 1
                    gTy = gTy + int(q_h + 4)
                    if qc == 1:
                        gTx = gTx + 20
                q_w, q_h = draw.textsize("- "+quote.quote_author, font=self.fonts.medium)
                gTx = int(self.screen_size[0]/2) - int(q_w/2)
                gTy = gTy - 5
                draw.text((gTx, gTy), "- "+quote.quote_author, font=self.fonts.medium, fill=gray)
                gTy = gTy + int(quote_icon.size[1]+10)
            ###########################
            # End of Quote of the day
            ###########################
        else:
            print("Quote feature :OFF")

                
        # Preparing for Garbage screens here.
        # Set Garbbage Day vaiables

                ######
            ##############
            ##  #  #  # ##
            ##  #  #  # ##
            ##  #  #  # ##
            ##  #  #  # ##
            ##  #  #  # ##
            ##############

        if self.cfg_data['garbage_schedule'] == "TRUE":

            # Setting up Garabage Variables          
            garbage_vars = dict()
            garbage_vars=get_garbage_config_data("garbage_schedules.ini")
            g_data = get_garbage_status()

            is_garbage_tomorrow = (g_data.landfill_prepapre, g_data.recycle_prepare, g_data.compost_prepare, g_data.dumpster_prepapre)
            is_garbage_today = (g_data.landfill, g_data.recycle, g_data.compost, g_data.xmas_tree, g_data.dumpster)
            # Clear the space below the comic - in case of Garbage
            if 1 in is_garbage_today or 1 in is_garbage_tomorrow :
                if gTy > int(self.boxes.next_days[0].pos_y + 14):
                    print("Clearing the bottom space for instructions...")
                    gCx = 0
                    gCy= int(self.boxes.next_days[0].pos_y +1)
                    comic_bottom = Image.open("icons/comic_bottom.png")
                    while gCx < self.screen_size[0] :
                        img.paste(comic_bottom,(gCx, gCy))
                        gCx = gCx + comic_bottom.size[0]
                    gTy = int(self.boxes.next_days[0].pos_y + 14)
                else :
                    draw.line([(0, gTy), (WIDTH, gTy)], gray)
                    print("Garbage schedule : Drawing a line to separate today")
                    gTy = gTy + 5

            else:
                print("Garbage schedule : No garbage schedules found, skipping...")

            garbage_collection_hour = int(garbage_vars['all-collection-time-over-id'])
            comparetime = currenttime.replace(hour=garbage_collection_hour, minute=0)

            gTx = 10 + X_OFFSET
            gx = 50
            gy = self.screen_size[1] - 280

            # Show the Calendar Icon
            cal_todo_icon = Image.open("icons/reminder_icon.png")

            if 1 in is_garbage_today :
                print("Garbage schedule : there is garbage today")
                img.paste(cal_todo_icon,(gTx, gTy))
                gTx = gTx + int( cal_todo_icon.size[0] + 8 )
                gTy = gTy - 8
                if currenttime <= comparetime:
                    g_image_end_icon = Image.open('icons/garbage_icons_garbagetruck.png')
                    g_string = garbage_vars['all-garbage-time-message-today-id']
                    g_sub_sting = garbage_vars['all-garbage-collect-message-id']
                    if g_data.landfill == 1:
                        g_string = g_string + " "+garbage_vars['landfill_title-id']
                    if g_data.recycle == 1:
                        g_string = g_string + " & "+garbage_vars['recycle_title-id']
                    if g_data.compost == 1:
                        g_string = g_string + " & "+garbage_vars['compost_title-id']
                    if g_data.dumpster == 1:
                        g_string = g_string + " & "+garbage_vars['dumpster_title-id']
                    if g_data.xmas_tree == 1:
                        g_string = g_string + " & "+garbage_vars['holiday-tree-schedule_title-id']
                    g_string = g_string + " " + garbage_vars['all-garbage-time-message-end-id']
                else:
                    g_image_end_icon = Image.open('icons/garbage_icons_garage.png')
                    g_string = garbage_vars['all-collection-time-over-message-line1-id']
                    g_sub_sting = garbage_vars['all-collection-time-over-message-line2-id']
                #print("Now trying to slice the text in chunks")
                print("Text is "+str(len(g_string)+" max is "+str(self.max_chars)))
                test_t_w, test_t_h = draw.textsize(g_string, font=self.fonts.medium)
                text_max = test_t_w
                text_line_max = self.max_chars
                text_line = []
                textbuffer = ""
                #Split the quote into words in an array
                schedule_words = g_string.split()
                wl = len(g_string)
                #See if the total is larger than the text_line_max value set.
                if text_max > text_line_max:
                    l = 0
                    ql = len(schedule_words)
                    while l < ql:
                        textbuffer = textbuffer + schedule_words[l] + " "
                        l += 1
                        test_t_w, test_t_h = draw.textsize(g_string, font=self.fonts.medium)
                        if test_t_w > text_line_max:
                            text_line.append(textbuffer)
                            textbuffer = ""
                    if (len(textbuffer)):
                        text_line.append(textbuffer)    
                else :
                    text_line.append(g_string)
                # Get number of arrays generated    
                qs = len(text_line)          
                qc = 0
                tg_w, tg_h = draw.textsize(text_line[0], font=self.fonts.medium)
                while qc < qs:
                    draw.text((gTx, gTy), text_line[qc], font=self.fonts.medium, fill=black)
                    qc += 1
                    gTy = gTy + int(tg_h)
                g_all_prepare = g_sub_sting

                if (len(g_sub_sting)) < self.max_chars :
                    draw.text((gTx, gTy), g_sub_sting, font=self.fonts.medium, fill=gray)
                    gTy = gTy + int(cal_todo_icon.size[1]+4)
                
                # Now add the icons in sequence below the Schedule text
                # Show the truck icon at the very right.
                gTx = int(self.screen_size[0] - int(g_image_end_icon.size[0])) - 10
                img.paste(g_image_end_icon, (gTx, gTy))
                # Add the arrows icon poiting to the street
                g_image_icon = Image.open('icons/garbage_icons_arrows.png')
                gTx = gTx - (int(g_image_icon.size[0])+10)
                img.paste(g_image_icon, (gTx, gTy))
                gTx = gTx - (int(g_image_icon.size[0])+10)
                if g_data.xmas_tree == 1:
                    g_image_icon = Image.open('icons/garbage_icons_holiday.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
                if g_data.dumpster == 1:
                    g_image_icon = Image.open('icons/garbage_icons_dumpster.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
                if g_data.compost == 1:
                    g_image_icon = Image.open('icons/garbage_icons_compost.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
                if g_data.recycle == 1:
                    g_image_icon = Image.open('icons/garbage_icons_recycle.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
                if g_data.landfill == 1:
                    g_image_icon = Image.open('icons/garbage_icons_landfill.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
                gTy = gTy + int(cal_todo_icon.size[1]+20)
            #else:
                #print("Garbage schedule : there is no garbage today")

            if 1 in is_garbage_tomorrow :
                cal_todo_icon = Image.open("icons/reminder_tomorrow_icon.png")
                gTx = 10 + X_OFFSET
                print("Garbage schedule : there is garbage tomorrow")
                if 1 in is_garbage_today :
                    draw.line([(0, gTy), (WIDTH, gTy)], gray)
                    print("Drawing a line to separate today and tomorrow")
                    gTy = gTy + 5
                img.paste(cal_todo_icon,(gTx, gTy))
                gTx = gTx + int( cal_todo_icon.size[0] + 8 )
                gTy = gTy - 8
                #Build the garbage schedule reminder string
                g_string = garbage_vars['all-garbage-time-message-tomorrow-id']
                if g_data.landfill_prepapre == 1:
                    g_string = g_string + " "+garbage_vars['landfill_title-id']
                if g_data.recycle_prepare == 1:
                    g_string = g_string + " & "+garbage_vars['recycle_title-id']
                if g_data.compost_prepare == 1:
                    g_string = g_string + " & "+garbage_vars['compost_title-id']
                if g_data.dumpster_prepapre == 1:
                    g_string = g_string + " & "+garbage_vars['dumpster_title-id']
                g_string = g_string + " " + garbage_vars['all-garbage-time-message-end-id']

                #print("Now trying to slice the text in chunks")
                test_t_w, test_t_h = draw.textsize(g_string, font=self.fonts.medium)
                text_max = test_t_w
                text_line_max = self.max_chars
                text_line = []
                textbuffer = ""
                #Split the quote into words in an array
                schedule_words = g_string.split()
                wl = len(g_string)
                #See if the total is larger than the text_line_max value set.
                if text_max > text_line_max:
                    l = 0
                    ql = len(schedule_words)
                    while l < ql:
                        textbuffer = textbuffer + schedule_words[l] + " "
                        l += 1
                        test_t_w, test_t_h = draw.textsize(g_string, font=self.fonts.medium)
                        if test_t_w > text_line_max:
                            text_line.append(textbuffer)
                            textbuffer = ""
                    if (len(textbuffer)):
                        text_line.append(textbuffer)    
                else :
                    text_line.append(g_string)
                # Get number of arrays generated    
                qs = len(text_line)          
                qc = 0
                tg_w, tg_h = draw.textsize(text_line[0], font=self.fonts.medium)
                while qc < qs:
                    draw.text((gTx, gTy), text_line[qc], font=self.fonts.medium, fill=black)
                    qc += 1
                    gTy = gTy + int(tg_h)
                g_all_prepare = garbage_vars['all-garbage-prepare-message-id']

                if (len(g_all_prepare)) < self.max_chars :
                    draw.text((gTx, gTy), g_all_prepare, font=self.fonts.medium, fill=gray)
                    # Now add the icons in sequence below the Schedule text
                    gTy = gTy + int(cal_todo_icon.size[1]+4)
                # Show the street icon at the very right.
                g_image_end_icon = Image.open('icons/garbage_icons_trees.png')
                gTx = int(self.screen_size[0] - int(g_image_end_icon.size[0])) - 10
                img.paste(g_image_end_icon, (gTx, gTy))
                # Add the arrows icon poiting to the street
                gTx = gTx - (int(g_image_end_icon.size[0])+10)
                g_image_icon = Image.open('icons/garbage_icons_arrows.png')
                img.paste(g_image_icon, (gTx, gTy))
                gTx = gTx - (int(g_image_icon.size[0])+10)
                

                if g_data.dumpster_prepapre == 1:
                    g_image_icon = Image.open('icons/garbage_icons_dumpster.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)

                if g_data.compost_prepare == 1:
                    g_image_icon = Image.open('icons/garbage_icons_compost.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)

                if g_data.recycle_prepare == 1:
                    g_image_icon = Image.open('icons/garbage_icons_recycle.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)

                if g_data.landfill_prepapre == 1:
                    g_image_icon = Image.open('icons/garbage_icons_landfill.png')
                    img.paste(g_image_icon, (gTx, gTy))
                    gTx = gTx - int(g_image_icon.size[1]+4)
            #else:
                #print("Garbage schedule : there is no garbage tomorrow")
                                
        else:
            print("Garbage schedule : OFF")
        
        # Print footer Last updated @
        footer = "Last refresh @ " + datetime.now().strftime("%H:%M")
        footer_w, footer_h = draw.textsize(footer, font=self.fonts.small)
        x = ( int(self.screen_size[0])/2 ) - (int(footer_w) / 2) + X_OFFSET
        y = int(self.screen_size[1])
        y = y - (int(footer_h) + 15)
        print("Footer: x "+str(x)+" y "+str(y))
        draw.text((x, y), footer, font=self.fonts.small, fill=gray)
      
        # battery level
        if "linux" in platform:
            bat_percent = get_battery_level()
            bat_chrg_state = get_battery_state()
            print("KoboHUB : Battery : "+str(bat_percent)+" - "+bat_chrg_state)
            #Check if battery is at 100%
            if int(bat_percent) == 100 :
               b_image_batt = Image.open('icons/batt100_32x20.png')
               bicon_x = (self.screen_size[0] - (b_image_batt.size[0]+8))
               img.paste(b_image_batt, (bicon_x, 5))
            if int(bat_percent) < 100 :
               b_image_batt = Image.open('icons/batt32x20.png')
               bicon_x = (self.screen_size[0] - (b_image_batt.size[0]+8))
               img.paste(b_image_batt, (bicon_x, 5))
               bat_w, bat_h = draw.textsize(str(bat_percent), font=self.fonts.micro)
               draw.text( ((bicon_x + 6), 8), str(bat_percent), font=self.fonts.micro, fill=black)
            if bat_chrg_state in ["Charging", "Not charging"] :
               b_image_chrg = Image.open('icons/chrg32x20.png')
               bicon_x = (self.screen_size[0] - (b_image_chrg.size[0]+8))
               img.paste(b_image_chrg, (bicon_x, 5))

        # ip address
        # print("KoboHUB : IP Address is: "+self.ip_address)
        wifi_icon_x = bicon_x - 24
        if self.ip_address != "1.1.1.1" :
            b_image_wifi_on = Image.open('icons/wifi_on.png')
            img.paste(b_image_wifi_on, (wifi_icon_x, 5))
        else:
            b_image_wifi_off = Image.open('icons/wifi_off.png')
            img.paste(b_image_wifi_off, (wifi_icon_x, 5))

        if "linux" in platform:
            img.save(tempfile.gettempdir() + "/img.bmp")
            return bytes(tempfile.gettempdir() + "/img.bmp", 'utf-8')
        else:
            img.save(tempfile.gettempdir() + "\\img.bmp")
            return bytes(tempfile.gettempdir() + "\\img.bmp", 'utf-8')

    def update(self):
        global kobo_blight

        screen_rotation = get_screen_orientation()
        #screen_size = get_kobo_screen_size()
        if screen_rotation == "PORTRAIT" :
            ticker_x = int(self.screen_size[0] - 175)
        else:
            ticker_x = int(self.screen_size[0] - 175)
            #ticker_x = 840

        ticker_image_file = 'icons/ticker_loading.png'
        ticker_os_cmd ="fbink -q --image file="+ticker_image_file+",x="+str(ticker_x)+",y=5 > /dev/null"
        os.system(ticker_os_cmd)

        try:
            self.weather.current = self.weather_fetcher.get_weather_current()
            self.weather.forecast = self.weather_fetcher.get_weather_forecast()
        except Exception as e:
            # Something went wrong while getting API Data, try again later.
            print("Weather : Failed to get weather data:\r\n" + str(e))
            return
        image = self._create_image()
        print("KoboHUB : Drawing image")
        
        if len(self.backlit_settings_data) == 24 and self.cfg_data['koboHUB-backlight'] == "TRUE":
            target_light = int(self.backlit_settings_data[int(datetime.now().strftime("%H"))])
            print("KoboHUB : Setting Backlight to configured value "+str(target_light)+" for "+datetime.now().strftime("%H"))
            kobo_blight = setBacklight (kobo_blight, target_light)

        
        rect = ffi.new("FBInkRect *")
        rect.top = 0
        rect.left = 0
        rect.width = 0
        rect.height = 0
        if "linux" in platform:
            fbink_version = ffi.string(fbink.fbink_version()).decode("ascii")
            fbink_version:str
            fbink_version = fbink_version.split(' ')[0]
            fbink_version = fbink_version.split('v')[1]
            major = fbink_version.split('.')[0]
            minor = fbink_version.split('.')[1]
            fbink_version = int(major)*100 + int(minor)
            if fbink_version >= 124:
                fbink.fbink_cls(self.fbfd, self.fbink_cfg, rect, 0)
            else:
                fbink.fbink_cls(self.fbfd, self.fbink_cfg, rect)

        fbink.fbink_print_image(self.fbfd, image, 0, 0, self.fbink_cfg)


def setBacklight (light_start, light_target):

 if light_start == light_target :
    print("KoboHUB : Dim of light skipped, ",light_start)
    return light_start

 dim = light_start
 dim_to = light_target
 dim_c = 0
 os_cmd = "./frontlight "+str(light_start)
 
 if light_target > light_start :
  dim_range = light_target - light_start
  print("KoboHUB : Fading up from ",dim," to ",light_target)

  for dim_c in range(dim_range):
     os.system(os_cmd)
     os_cmd = "./frontlight "+str(dim)
     dim = dim + 1
  return dim

 if light_target < light_start :
  dim_range = light_start - light_target
  print("KoboHUB : Fading dowm from ",dim," to ",light_target)

  for dim_c in range(dim_range):
     os.system(os_cmd)
     os_cmd = "./frontlight "+str(dim)
     dim = dim -1
  return dim

def splash_loading(splash_wait:int):
    print("\nKoboHUB : Showing welcome screen\n")
    os.system("fbink -q --flash > /dev/null")
    splash_image_file = 'icons/loading.png'
    splash_os_cmd ="fbink -q -g file="+splash_image_file+",halign=CENTER,valign=CENTER > /dev/null"
    os.system(splash_os_cmd)
    time.sleep(splash_wait)
    os.system("fbink -q --flash > /dev/null")

def get_screen_orientation():
    s_orientation ="unknwon"
    with open("/sys/class/graphics/fb0/subsystem/fb0/rotate") as file:
        screen_orientation = file.readline() 
        screen_orientation = screen_orientation.rstrip('\n')
        #print("Raw screen readout is "+str(screen_orientation))
    if int(screen_orientation) == 2 or int(screen_orientation) == 1:
        s_orientation = "LANDSCAPE"
    if int(screen_orientation) == 0 or int(screen_orientation) == 3:
        s_orientation = "PORTRAIT"
    #print("Screen orientation is", s_orientation)
    return s_orientation

def get_kobo_screen_size():
    with open("/sys/class/graphics/fb0/subsystem/fb0/virtual_size") as file:
        vsize = file.readline() 
        vsize = vsize.rstrip('\n')
        vsize = vsize.split(",")
        vrsize = []
        vrsize.append(int(vsize[0]))
        vrsize.append(int(vsize[1]))
    return vrsize

def set_screen_orientation(orientation:str):
    if orientation == "PORTRAIT" :      
        os.system("echo 3 > /sys/class/graphics/fb0/subsystem/fb0/rotate")
        return "PORTRAIT"
    if orientation == "LANDSCAPE" :
        os.system("echo 2 > /sys/class/graphics/fb0/subsystem/fb0/rotate")
        return "LANDSCAPE"

def get_battery_level():
    with open("/sys/class/power_supply/mc13892_bat/capacity") as file:
        bat_percent = file.readline()
        bat_percent = bat_percent.rstrip('\n')
    return bat_percent
        
def get_battery_state():
    # Charging state Not charging, Discharging, Charging
    with open("/sys/class/power_supply/mc13892_bat/status") as file:                                               
        bat_chrg_state = file.readline()
        bat_chrg_state = bat_chrg_state.rstrip('\n')
    return bat_chrg_state

def main():
    global day_check
       

    screen_rotation = get_screen_orientation()
    screen_size = get_kobo_screen_size()

    print("koboHUB started!\n\n")
  
    # fbink configuration
    fbink_cfg = ffi.new("FBInkConfig *")
    fbfd = fbink.fbink_open()
    fbink.fbink_init(fbfd, fbink_cfg)
    state = ffi.new("FBInkState *")
    fbink.fbink_get_state(fbink_cfg, state)

    if "linux" in platform:
        screen_size = get_kobo_screen_size()
    else:
        screen_size = (768, 1024)
    
    splash_loading(2)
    cfg_data = dict()
    cfg_file_data = get_config_data(CONFIGFILE,1)
    cfg_data['screen-orientation'] = cfg_file_data['screen-orientation_id']
    cfg_data['koboHUB-refresh-seconds'] = cfg_file_data['koboHUB-refresh-seconds_id']
    print("KoboHUB : Refresh mutipler set to "+cfg_data['koboHUB-refresh-seconds']+" seconds * 5")
    hub_refresh = int(cfg_data['koboHUB-refresh-seconds']) * 5 /60
    print("KoboHUB : Refreshes every "+str(hub_refresh)+" minutes")
    screen_rotation=set_screen_orientation(cfg_data['screen-orientation'])
    print("KoboHUB : Setting screen orientation to: "+screen_rotation)
    print("KoboHUB : Screen size is: "+str(screen_size[0])+" by "+str(screen_size[1]))
       
    if "linux" in platform:
        call(["hostname", "kobo"])

    print("KoboHUB : IP Address is : "+wait_for_wifi())

    if "linux" in platform:
        print("\nKoboHUB : Shutting down Kobo Springboards...\n\n")
        os.system("fbink -q --clear --flash")
        call(["killall", "-TERM", "nickel", "hindenburg", "sickel", "fickel"])
        print("\n")
    kobohub = koboHUB()
    counter = 0



    ticker_image = Image.open('icons/ticker_loading.png')
    #Clear the screen well before start
    day_check = datetime.now().strftime("%d-%m-%Y")
    hour_check = datetime.now().strftime("%H")
    try:
        while True:
            if screen_rotation == "PORTRAIT" :
                ticker_x = int(screen_size[0]) -175
            else:
                screen_size = get_kobo_screen_size()
                ticker_x = int(screen_size[0]) - 175
            #print("Comparing ",day_check," with ",datetime.now().strftime("%d-%m-%Y"))
            if hour_check != datetime.now().strftime("%H") :
                print("KoboHUB : Cleaninig the e-ink for the hour")
                os.system("fbink -q --flash > /dev/null")
                hour_check = datetime.now().strftime("%H")
            ticker = 1
            ticker_time = int(cfg_data['koboHUB-refresh-seconds'])
            ticker_time = (ticker_time /60) * 5
            print("\nKoboHUB : update nr. " + str(counter))
            kobohub.ip_address = wait_for_wifi()
            kobohub.update()

            if int(get_battery_level()) < 10 :
                print("KoboHUB : Warning Battery low!")
                warn_image_file = 'icons/LowBattWarning.png'
                warn_os_cmd ="fbink -q -g file="+warn_image_file+",halign=CENTER,valign=CENTER > /dev/null"
                os.system(warn_os_cmd)

            print("KoboHUB : Sleeping")
            # sleep 5 min, but ping every 30 seconds... maybe the wifi will stay on
            for sleep in range(5):
                ticker_image_file = 'icons/ticker_'+str(ticker)+'.png'
                ticker_os_cmd ="fbink -q --image file="+ticker_image_file+",x="+str(ticker_x)+",y=5 > /dev/null"
                os.system(ticker_os_cmd)
                ticker = ticker +1
                print("Refresh in: "+str(ticker_time)+" minues ; round :"+str(counter))
                time.sleep(int(cfg_data['koboHUB-refresh-seconds']))
                ticker_time -= 1
                #os.system("ping -c 1 -q www.google.com > /dev/null")
            counter += 1
    finally:
        fbink.fbink_close(kobohub.fbfd)

if __name__ == "__main__":
    main()
