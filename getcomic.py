# -*- coding: utf-8 -*-
"""
Created on Wed May 20 23:20:53 2020

@author: mazdoc, kjerk
"""

### Comic name comes from the URL and needs to be exactly as it is in the URL
### You should also supply the first date of the comic.
### Calvin and Hobbes Started on November 18, 1985 ie 1985-11-18
###
### foxtrot/1988/04/11

from datetime import datetime, date
import datetime
import os
import requests
import time
from urllib.request import urlopen
from dataclasses import dataclass

@dataclass
class comic_summary:
    comic_title: str
    comic_url :str

def getComicFile(comictitle:str):
  #print("Received "+comictitle)
  if comictitle == "none" :
    comic_data = comic_summary(comic_title="Notitle", comic_url="Nofile")
    return comic_data
  # Config
  base_url = 'https://www.gocomics.com/{}/{}/{}/{}'
  comic_name = comictitle
  save_dir = './comics/'+comic_name
  remove_dir = 'comics/'+comic_name
  #first_date = "2019-01-01"
  requestWaitMs = 500  # Be kind when scraping

  cdate = date.today()
  cdate.replace(year=2020) # Rolling back time a little to catch more comics
  tdate = cdate.strftime("%Y-%m-%d")
  first_date = tdate

  # Init Save Dir
  if not os.path.isdir(save_dir):
      os.makedirs(save_dir)
  
  file_list = os.listdir(save_dir)
  file_count = len(file_list)
  date_cursor = datetime.date(int(first_date[0:4]), int(first_date[5:7]), int(first_date[8:10]))
  print("Found ",file_count," files")

  #Check if we need to clean up, only keep the last 10
  if file_count > 10 :
    rf = 0
    while rf < 10:
        try:
            clean_file_name = remove_dir+"/"+file_list[rf]
            print("Deleting: "+clean_file_name)
            os.remove(clean_file_name)
        except OSError as error:
            print("There was an error.")
        rf += 1

  #    last_file_name = os.path.basename()
  #    date_cursor = datetime.date.fromisoformat(os.path.splitext(last_file_name)[0])
  #    print("Starting from checkpoint: {}".format(date_cursor))
  
  now = datetime.datetime.now()
  
  save_file_name = '{}.gif'.format(date_cursor)
  comicfilepath = save_dir+"/"+save_file_name
  print("Comic file to store: {}".format(save_file_name), end = '')
  url = base_url.format(comic_name,date_cursor.year,date_cursor.month,date_cursor.day)
  r = requests.get(url, allow_redirects=True)
  title = "unknown"
  
  '''
  page = requests.get(url, allow_redirects=True)
  html_bytes = page.text
  html = html_bytes.encode("UTF-8")
  #print(html)
  tl = len(html)
  title_index = html.find("<title>",0,tl)
  start_index = title_index + len("<title>")
  end_index = html.find("</title>")
  title = html[start_index:end_index]
  end_index = html.find("- GoComics")
  title = html[start_index:end_index]
  
  #print("Title is: ")
  #print(title)
  '''
  if os.path.isfile(comicfilepath) :
    print("File already exists, skipping download of comic")
    comicfilepath = comicfilepath.strip("./")
    comic_data = comic_summary(comic_title=title, comic_url=comicfilepath)
    return comic_data

  comic_data = comic_summary(comic_title="Notitle", comic_url="Nofile")
  if len(r.history) < 1:
      loc = int(r.text.find('https://assets.amuniversal.com/'))
      imgurl = r.text[loc:loc+63]
      imgr = requests.get(imgurl, allow_redirects=True)
      with open('{}/{}'.format(save_dir, save_file_name), 'wb') as fh:
          fh.write(imgr.content)
      print("")
      comicfilepath = save_dir+"/"+save_file_name
      comicfilepath = comicfilepath.strip("./")
      comic_data = comic_summary(comic_title=title, comic_url=comicfilepath)
      return comic_data
  else:
      print(" - redirected, comic probably doesn't exist")
      return comic_data
