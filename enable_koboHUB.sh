#!/bin/sh

APP_FOLDER="/mnt/onboard/.apps/koboHUB/"
INIT_SCRIPT_LOCAL="$APP_FOLDER/utils/init_script"
INIT_SCRIPT_REMOTE="/etc/init.d/koboHUB"

if [ ! -d $APP_FOLDER ]; then
    echo "Please move the application to the correct folder: $APP_FOLDER"
    exit -1
fi
if [ ! -e "$APP_FOLDER/koboHUB.py" ]; then
    echo "Please move the application to the correct folder: $APP_FOLDER"
    exit -1
fi
cd $APP_FOLDER


# check if inittab already contains the yawk command
if grep -q "koboHUB" /etc/inittab; then

    echo "koboHUB Already enabled, skipping ahead..."
    exit -1
else
# add the command to start the yawk
    echo "::sysinit:/etc/init.d/koboHUB" >> /etc/inittab
    echo "koboHUB has been added to startup ..."
fi

echo
echo "The eReader will restart now..."
sleep 5
reboot


