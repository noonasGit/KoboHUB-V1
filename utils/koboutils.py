import sys
import os

def get_kobo_screen_size():
    with open("/sys/class/graphics/fb0/subsystem/fb0/virtual_size") as file:
        vsize = file.readline() 
        vsize = vsize.rstrip('\n')
        vsize = vsize.split(",")
        vrsize = []
        vrsize[0] = int(vsize[0])
        vrsize[1] = int(vsize[1])
    return vrsize

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

def set_screen_orientation(orientation:str):
    if orientation == "PORTRAIT" :      
        os.system("echo 3 > /sys/class/graphics/fb0/subsystem/fb0/rotate")
        return "PORTRAIT"
    if orientation == "LANDSCAPE" :
        os.system("echo 2 > /sys/class/graphics/fb0/subsystem/fb0/rotate")
        return "LANDSCAPE"

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

print("Screen orientatino is "+get_screen_orientation())
sz = get_kobo_screen_size()
#print(sz)
print("Screen size is "+str(sz[0])+" by "+str(sz[1]))