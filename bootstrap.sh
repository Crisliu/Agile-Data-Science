#
# Update & install dependencies
#
apt-get update && \
    apt-get install -y zip unzip curl bzip2 python-dev build-essential git libssl1.0.0 libssl-dev

#
# Install Java and setup ENV
#
apt-get install -y software-properties-common debconf-utils && \
    add-apt-repository -y ppa:webupd8team/java && \
    apt-get update && \
    echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections && \
    apt-get install -y oracle-java8-installer

export JAVA_HOME=/usr/lib/jvm/java-8-oracle
echo "export JAVA_HOME=/usr/lib/jvm/java-8-oracle" >> ~/.bash_profile

#
# Install Anaconda
#
curl -Lko /tmp/Anaconda3-4.2.0-Linux-x86_64.sh http://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
bash /tmp/Anaconda3-4.2.0-Linux-x86_64.sh -b -p ~/anaconda

export PATH=/root/anaconda/bin:$PATH
echo "export PATH=/root/anaconda/bin:$PATH" >> ~/.bash_profile

#
# Install Clone repo, install Python dependencies
#
git clone https://github.com/rjurney/Agile_Data_Code_2
cd /root/Agile_Data_Code_2
export PROJECT_HOME=/Agile_Data_Code_2
echo "export PROJECT_HOME=/Agile_Data_Code_2" >> ~/.bash_profile
pip install --upgrade pip && pip install -r requirements.txt
cd

#
# Install Hadoop
#
curl -Lko /tmp/hadoop-2.7.3.tar.gz http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
mkdir -p ~/hadoop && tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1

echo '# Hadoop environment setup' >> ~/.bash_profile
export HADOOP_HOME=$PROJECT_HOME/hadoop
echo 'export HADOOP_HOME=$PROJECT_HOME/hadoop' >> ~/.bash_profile
export PATH=$PATH:$HADOOP_HOME/bin
echo 'export PATH=$PATH:$HADOOP_HOME/bin' >> ~/.bash_profile
export HADOOP_CLASSPATH=$(hadoop classpath)
echo 'export HADOOP_CLASSPATH=$(hadoop classpath)' >> ~/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' >> ~/.bash_profile

#
# Install Spark
#
curl -Lko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz
mkdir -p ~/spark && tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C spark --strip-components=1

echo "" >> ~/.bash_profile
echo "# Spark environment setup" >> ~/.bash_profile
export SPARK_HOME=$PROJECT_HOME/spark
echo 'export SPARK_HOME=$PROJECT_HOME/spark' >> ~/.bash_profile
export HADOOP_CONF_DIR=$PROJECT_HOME/hadoop/etc/hadoop/
echo 'export HADOOP_CONF_DIR=$PROJECT_HOME/hadoop/etc/hadoop/' >> ~/.bash_profile
export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`
echo 'export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`' >> ~/.bash_profile
export PATH=$PATH:$SPARK_HOME/bin
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.bash_profile

# Have to set spark.io.compression.codec in Spark local mode
cp ~/spark/conf/spark-defaults.conf.template ~/spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' >> ~/spark/conf/spark-defaults.conf

# Give Spark 8GB of RAM, used Python3
echo "spark.driver.memory 8g" >> $SPARK_HOME/conf/spark-defaults.conf
echo "PYSPARK_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh
echo "PYSPARK_DRIVER_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh

# Setup log4j config to reduce logging output
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
sed -i 's/INFO/ERROR/g' $SPARK_HOME/conf/log4j.properties

#
# Install MongoDB and dependencies
#
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" > /etc/apt/sources.list.d/mongodb-org-3.4.list
apt-get update && apt-get install -y --allow-unauthenticated mongodb-org && mkdir -p /data/db

# run MongoDB as daemon
/usr/bin/mongod --fork --logpath /var/log/mongodb.log

# Get the MongoDB Java Driver
curl -Lko ~/Agile_Data_Code_2/lib/mongo-java-driver-3.4.0.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.0/mongo-java-driver-3.4.0.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
curl -Lko /tmp/mongo-hadoop-r1.5.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r1.5.2.tar.gz
mkdir ~/mongo-hadoop
tar -xvzf /tmp/mongo-hadoop-r1.5.2.tar.gz -C mongo-hadoop --strip-components=1

# Now build the mongo-hadoop-spark jars
cd ~/mongo-hadoop
./gradlew jar
cp ~/mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar ~/Agile_Data_Code_2/lib/
cp ~/mongo-hadoop/build/libs/mongo-hadoop-*.jar ~/Agile_Data_Code_2/lib/
cd

# Now build the pymongo_spark package
cd ~/mongo-hadoop/spark/src/main/python
python setup.py install
cp ~/mongo-hadoop/spark/src/main/python/pymongo_spark.py ~/Agile_Data_Code_2/lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' >> ~/.bash_profile
cd

rm -rf ~/mongo-hadoop

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
curl -Lko /tmp/elasticsearch-5.1.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.tar.gz
mkdir ~/elasticsearch
tar -xvzf /tmp/elasticsearch-5.1.1.tar.gz -C ~/elasticsearch --strip-components=1

# Run elasticsearch
~/elasticsearch/bin/elasticsearch -d # re-run if you shutdown your computer

# Install Elasticsearch for Hadoop
curl -Lko /tmp/elasticsearch-hadoop-5.1.1.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.1.1.zip
unzip /tmp/elasticsearch-hadoop-5.1.1.zip && mv ~/elasticsearch-hadoop-5.1.1 ~/elasticsearch-hadoop
cp ~/elasticsearch-hadoop/dist/elasticsearch-hadoop-5.1.1.jar ~/Agile_Data_Code_2/lib/
cp ~/elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.1.1.jar ~/Agile_Data_Code_2/lib/
echo "spark.speculation false" >> ~/spark/conf/spark-defaults.conf
rm -f /tmp/elasticsearch-hadoop-5.1.1.zip
rm -rf ~/elasticsearch-hadoop/conf/spark-defaults.conf

#
# Spark jar setup
#
echo "spark.jars ~/Agile_Data_Code_2/lib/mongo-hadoop-spark-1.5.2.jar,~/Agile_Data_Code_2/lib/mongo-java-driver-3.4.0.jar,~/Agile_Data_Code_2/lib/mongo-hadoop-1.5.2.jar,~/Agile_Data_Code_2/lib/elasticsearch-spark-20_2.10-5.1.1.jar,~/Agile_Data_Code_2/lib/snappy-java-1.1.2.6.jar,~/Agile_Data_Code_2/lib/lzo-hadoop-1.0.5.jar" >> ~/spark/conf/spark-defaults.conf

#
# Kafka install and setup
#
curl -Lko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
mkdir -p ~/kafka
tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C ~/kafka --strip-components=1 && rm -f /tmp/kafka_2.11-0.10.1.1.tgz

# Run zookeeper (which kafka depends on), then Kafka
~/kafka/bin/zookeeper-server-start.sh -daemon ~/kafka/config/zookeeper.properties
~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties

#
# Install and setup Airflow
#
pip install airflow
mkdir ~/airflow
mkdir ~/airflow/dags
mkdir ~/airflow/logs
mkdir ~/airflow/plugins
airflow initdb
airflow webserver -D
airflow scheduler -D

#
# Install and configure zeppelin
#
curl -Lko /tmp/zeppelin-0.6.2-bin-all.tgz http://www-us.apache.org/dist/zeppelin/zeppelin-0.6.2/zeppelin-0.6.2-bin-all.tgz
mkdir -p ~/zeppelin
tar -xvzf /tmp/zeppelin-0.6.2-bin-all.tgz -C ~/zeppelin --strip-components=1
rm -f /tmp/zeppelin-0.6.2-bin-all.tgz

# Configure Zeppelin
cp ~/zeppelin/conf/zeppelin-env.sh.template ~/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_HOME=~/spark" >> ~/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_MASTER=local" >> ~/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_CLASSPATH=" >> ~/zeppelin/conf/zeppelin-env.sh

#
# Get airplane data
#

# Get on-time records for all flights in 2015 - 273MB
curl -Lko $PROJECT_HOME/data/On_Time_On_Time_Performance_2015.csv.gz http://s3.amazonaws.com/agile_data_science/On_Time_On_Time_Performance_2015.csv.gz

# Get openflights data
curl -Lko /tmp/airports.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat
mv /tmp/airports.dat $PROJECT_HOME/data/airports.csv

curl -Lko /tmp/airlines.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
mv /tmp/airlines.dat $PROJECT_HOME/data/airlines.csv

curl -Lko /tmp/routes.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
mv /tmp/routes.dat $PROJECT_HOME/data/routes.csv

curl -Lko /tmp/countries.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat
mv /tmp/countries.dat $PROJECT_HOME/data/countries.csv

# Get FAA data
curl -Lko $PROJECT_HOME/data/aircraft.txt http://av-info.faa.gov/data/ACRef/tab/aircraft.txt
curl -Lko $PROJECT_HOME/data/ata.txt http://av-info.faa.gov/data/ACRef/tab/ata.txt
curl -Lko $PROJECT_HOME/data/compt.txt http://av-info.faa.gov/data/ACRef/tab/compt.txt
curl -Lko $PROJECT_HOME/data/engine.txt http://av-info.faa.gov/data/ACRef/tab/engine.txt
curl -Lko $PROJECT_HOME/data/prop.txt http://av-info.faa.gov/data/ACRef/tab/prop.txt

#
# Get weather data
#

cd $PROJECT_HOME/data

# Get the station master list as pipe-seperated-values
curl -Lko /tmp/wbanmasterlist.psv.zip http://www.ncdc.noaa.gov/homr/file/wbanmasterlist.psv.zip
unzip -o /tmp/wbanmasterlist.psv.zip
gzip wbanmasterlist.psv
rm -f /tmp/wbanmasterlist.psv.zip

# Get monthly files of daily summaries for all stations
# curl -Lko /tmp/ http://www.ncdc.noaa.gov/orders/qclcd/QCLCD201501.zip
for i in $(seq -w 1 12)
do
  curl -Lko /tmp/QCLCD2015${i}.zip http://www.ncdc.noaa.gov/orders/qclcd/QCLCD2015${i}.zip
  unzip -o /tmp/QCLCD2015${i}.zip
  gzip 2015${i}*.txt
  rm -f /tmp/QCLCD2015${i}.zip
done

cd

#
# Cleanup
#
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
