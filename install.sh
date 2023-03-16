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

# first, check if the config.ini exists
if [ ! -e "config.ini" ]; then
    # let's create it
	correct='n'
    while [ $correct != 'y' ]; do
        echo "unit is mentric or imperial"
        echo "Language is in international format (en, se etc.)"
        read -p "Enter your API key: " api
        read -p "Enter your city\'s ID: " city
        read -p "Preferred unit: " unit
        read -p "Weather langyage: " lang
        echo
        echo "Your API key is '$api'"
        echo "Your city ID is '$city'"
        echo "Your preferred unit is '$unit'"
        echo "Weather language is '$lang'"
        read -p "Correct? [yn] " correct
    done

    echo "[yawk]" > config.ini
    echo "ow-api-key=$api" >> config.ini
    echo "ow-city=$city" >> config.ini
    echo "ow-unit=$unit" >> config.ini
    echo "ow-language=$lang" >> config.ini
fi

# copy the automatic initializer
cp $INIT_SCRIPT_LOCAL $INIT_SCRIPT_REMOTE
chmod a+x $INIT_SCRIPT_REMOTE

# check if inittab already contains the koboHUB command
if grep -q "koboHUB" /etc/inittab; then
    # delete the line containing the koboHUB command
    sed -i '/koboHUB/d' /etc/inittab
fi
# add the command to start the koboHUB
echo "::sysinit:/etc/init.d/koboHUB" >> /etc/inittab

# check if the wifi is already set to autoscan
if grep -q "autoscan" /etc/wpa_supplicant/wpa_supplicant.conf.template; then
    # delete the line containing te autoscan config
    sed -i '/autoscan/d' /etc/wpa_supplicant/wpa_supplicant.conf.template
fi
# add the autoscan back
echo "autoscan=exponential:3:60" >> /etc/wpa_supplicant/wpa_supplicant.conf.template

# add the option to not kill the wifi
echo >> "/mnt/onboard/.kobo/Kobo/Kobo eReader.conf"
echo "[DeveloperSettings]" >> "/mnt/onboard/.kobo/Kobo/Kobo eReader.conf"
echo "ForceWifiOn=true" >> "/mnt/onboard/.kobo/Kobo/Kobo eReader.conf"

echo
echo "All Good! The eReader will restart now..."
sleep 5
reboot