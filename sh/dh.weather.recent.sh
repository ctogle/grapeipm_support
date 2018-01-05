#!/bin/bash
export PATH=$PATH:/usr/local/bin
# n = # of days to go back
n=2
# parse incoming weather files
cd /data/model/weather/grapeipm_support
./convert.py  -o /var/www/incoming/weather/formatted/csci_weather.csv -s "`date -d"-$n days" "+%Y-%m-%d %H:%M:%S"`" -e "`date "+%Y-%m-%d %H:%M:%S"`" -u config/grapeipm.cfg -w

# push them to Drupal
cd /var/www/d.live
drush scr modules/dh_weather/src/import.dhw.php

