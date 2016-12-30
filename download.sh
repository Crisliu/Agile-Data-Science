#!/usr/bin/env bash
#
# Script to download data for book
#
mkdir data

#
# Get airplane data
#

# Get on-time records for all flights in 2015 - 273MB
curl -Lko data/On_Time_On_Time_Performance_2015.csv.gz http://s3.amazonaws.com/agile_data_science/On_Time_On_Time_Performance_2015.csv.gz

# Get openflights data
curl -Lko /tmp/airports.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat
mv /tmp/airports.dat data/airports.csv

curl -Lko /tmp/airlines.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
mv /tmp/airlines.dat data/airlines.csv

curl -Lko /tmp/routes.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
mv /tmp/routes.dat data/routes.csv

curl -Lko /tmp/countries.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat
mv /tmp/countries.dat data/countries.csv

# Get FAA data
curl -Lko data/aircraft.txt http://av-info.faa.gov/data/ACRef/tab/aircraft.txt
curl -Lko data/ata.txt http://av-info.faa.gov/data/ACRef/tab/ata.txt
curl -Lko data/compt.txt http://av-info.faa.gov/data/ACRef/tab/compt.txt
curl -Lko data/engine.txt http://av-info.faa.gov/data/ACRef/tab/engine.txt
curl -Lko data/prop.txt http://av-info.faa.gov/data/ACRef/tab/prop.txt

#
# Get weather data
#

cd data

# Get the station master list as pipe-seperated-values
curl -Lko /tmp/wbanmasterlist.psv.zip http://www.ncdc.noaa.gov/homr/file/wbanmasterlist.psv.zip
unzip /tmp/wbanmasterlist.psv.zip

# Get monthly files of daily summaries for all stations
# curl -Lko /tmp/ http://www.ncdc.noaa.gov/orders/qclcd/QCLCD201501.zip
for i in $(seq -w 1 12)
do
  curl -Lko /tmp/QCLCD2015${i}.zip http://www.ncdc.noaa.gov/orders/qclcd/QCLCD2015${i}.zip
  unzip /tmp/QCLCD2015${i}.zip
done

cd ..
