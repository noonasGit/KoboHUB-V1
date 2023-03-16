#!/bin/sh

APP_FOLDER="/mnt/onboard/.apps/koboHUB/"

if [ ! -d $APP_FOLDER ]; then
    echo "Application is not present or not in the correct folder: $APP_FOLDER"
    exit -1
fi

# check if inittab already contains the yawk command
if grep -q "koboHUB" /etc/inittab; then
    # delete the line containing the yawk command
    sed -i '/koboHUB/d' /etc/inittab
fi

echo "koboHUB Disabled, The eReader will restart now..."
sleep 10
reboot