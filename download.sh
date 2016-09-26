#
# Script to download data for book
#
mkdir data

#
# Get airplane data
#

# Get on-time records for all flights in 2015 - 273MB
wget -P data/ http://s3.amazonaws.com/agile_data_science/On_Time_On_Time_Performance_2015.csv.gz

# Get openflights data
wget -P /tmp/ https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat
mv /tmp/airports.dat data/airports.csv

wget -P /tmp/ https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
mv /tmp/airlines.dat data/airlines.csv

wget -P /tmp/ https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
mv /tmp/routes.dat data/routes.csv

wget -P /tmp/ https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat
mv /tmp/countries.dat data/countries.csv

# Get FAA data
wget -P data/ http://av-info.faa.gov/data/ACRef/tab/aircraft.txt
wget -P data/ http://av-info.faa.gov/data/ACRef/tab/ata.txt
wget -P data/ http://av-info.faa.gov/data/ACRef/tab/compt.txt
wget -P data/ http://av-info.faa.gov/data/ACRef/tab/engine.txt
wget -P data/ http://av-info.faa.gov/data/ACRef/tab/prop.txt

#
# Get weather data
#

cd data

# Get the station master list as pipe-seperated-values
wget -P /tmp/ http://www.ncdc.noaa.gov/homr/file/wbanmasterlist.psv.zip
unzip /tmp/wbanmasterlist.psv.zip

# Get monthly files of daily summaries for all stations
# wget -P /tmp/ http://www.ncdc.noaa.gov/orders/qclcd/QCLCD201501.zip
for i in $(seq -w 1 12)
do
  wget -P /tmp/ http://www.ncdc.noaa.gov/orders/qclcd/QCLCD2015${i}.zip
  unzip /tmp/QCLCD2015${i}.zip
done

cd ..
