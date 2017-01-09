#
# Update & install dependencies
#
sudo apt-get update
sudo apt-get install -y zip unzip curl bzip2 python-dev build-essential git libssl1.0.0 libssl-dev

#
# Install Java and setup ENV
#
sudo apt-get install -y software-properties-common debconf-utils python-software-properties
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install -y oracle-java8-installer oracle-java8-set-default

export JAVA_HOME=/usr/lib/jvm/java-8-oracle
echo "export JAVA_HOME=/usr/lib/jvm/java-8-oracle" | sudo tee -a /home/vagrant/.bash_profile

#
# Install Anaconda
#
curl -Lko /tmp/Anaconda3-4.2.0-Linux-x86_64.sh http://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
chmod +x /tmp/Anaconda3-4.2.0-Linux-x86_64.sh
/tmp/Anaconda3-4.2.0-Linux-x86_64.sh -b -p /home/vagrant/anaconda

export PATH=/home/vagrant/anaconda/bin:$PATH
echo 'export PATH=/home/vagrant/anaconda/bin:$PATH' | sudo tee -a /home/vagrant/.bash_profile

#
# Install Clone repo, install Python dependencies
#
cd /home/vagrant
git clone https://github.com/rjurney/Agile_Data_Code_2
cd /home/vagrant/Agile_Data_Code_2
export PROJECT_HOME=/home/vagrant/Agile_Data_Code_2
echo "export PROJECT_HOME=/home/vagrant/Agile_Data_Code_2" >> /home/vagrant/.bash_profile
pip install --upgrade pip
pip install -r requirements.txt
sudo chown -R vagrant /home/vagrant/Agile_Data_Code_2
sudo chgrp -R vagrant /home/vagrant/Agile_Data_Code_2
cd /home/vagrant

#
# Install Hadoop
#
curl -Lko /tmp/hadoop-2.7.3.tar.gz http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
mkdir -p /home/vagrant/hadoop
tar -xvf /tmp/hadoop-2.7.3.tar.gz -C /home/vagrant/hadoop --strip-components=1

echo '# Hadoop environment setup' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_HOME=/home/vagrant/hadoop
echo 'export HADOOP_HOME=/home/vagrant/hadoop' | sudo tee -a /home/vagrant/.bash_profile
export PATH=$PATH:$HADOOP_HOME/bin
echo 'export PATH=$PATH:$HADOOP_HOME/bin' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CLASSPATH=$(hadoop classpath)
echo 'export HADOOP_CLASSPATH=$(hadoop classpath)' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' | sudo tee -a /home/vagrant/.bash_profile

# Give to vagrant
sudo chown -R vagrant /home/vagrant/hadoop
sudo chgrp -R vagrant /home/vagrant/hadoop

#
# Install Spark
#
curl -Lko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz
mkdir -p /home/vagrant/spark
tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C /home/vagrant/spark --strip-components=1

echo "" >> /home/vagrant/.bash_profile
echo "# Spark environment setup" | sudo tee -a /home/vagrant/.bash_profile
export SPARK_HOME=/home/vagrant/spark
echo 'export SPARK_HOME=/home/vagrant/spark' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/' | sudo tee -a /home/vagrant/.bash_profile
export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`
echo 'export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`' | sudo tee -a /home/vagrant/.bash_profile
export PATH=$PATH:$SPARK_HOME/bin
echo 'export PATH=$PATH:$SPARK_HOME/bin' | sudo tee -a /home/vagrant/.bash_profile

# Have to set spark.io.compression.codec in Spark local mode
cp /home/vagrant/spark/conf/spark-defaults.conf.template /home/vagrant/spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf

# Give Spark 8GB of RAM, used Python3
echo "spark.driver.memory 8g" | sudo tee -a $SPARK_HOME/conf/spark-defaults.conf
echo "PYSPARK_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh
echo "PYSPARK_DRIVER_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh

# Setup log4j config to reduce logging output
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
sed -i 's/INFO/ERROR/g' $SPARK_HOME/conf/log4j.properties

# Give to vagrant
sudo chown -R vagrant /home/vagrant/spark
sudo chgrp -R vagrant /home/vagrant/spark

#
# Install MongoDB and dependencies
#
#echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
#sudo apt-get update
#sudo apt-get install -y --allow-unauthenticated mongodb-org-shell mongodb-org-server mongodb-org-mongos mongodb-org-tools mongodb-org
sudo apt-get install -y mongodb
sudo mkdir -p /data/db
sudo chown -R mongodb /data/db
sudo chgrp -R mongodb /data/db

# run MongoDB as daemon
sudo /usr/bin/mongod --fork --logpath /var/log/mongodb.log

# Get the MongoDB Java Driver
curl -Lko /home/vagrant/Agile_Data_Code_2/lib/mongo-java-driver-3.4.0.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.0/mongo-java-driver-3.4.0.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
curl -Lko /tmp/mongo-hadoop-r1.5.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r1.5.2.tar.gz
mkdir /home/vagrant/mongo-hadoop
tar -xvzf /tmp/mongo-hadoop-r1.5.2.tar.gz -C /home/vagrant/mongo-hadoop --strip-components=1

# Now build the mongo-hadoop-spark jars
cd /home/vagrant/mongo-hadoop
./gradlew jar
cp /home/vagrant/mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar /home/vagrant/Agile_Data_Code_2/lib/
cp /home/vagrant/mongo-hadoop/build/libs/mongo-hadoop-*.jar /home/vagrant/Agile_Data_Code_2/lib/
cd /home/vagrant

# Now build the pymongo_spark package
cd /home/vagrant/mongo-hadoop/spark/src/main/python
python setup.py install
cp /home/vagrant/mongo-hadoop/spark/src/main/python/pymongo_spark.py /home/vagrant/Agile_Data_Code_2/lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' | sudo tee -a /home/vagrant/.bash_profile
cd /home/vagrant

rm -rf /home/vagrant/mongo-hadoop

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
curl -Lko /tmp/elasticsearch-5.1.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.tar.gz
mkdir /home/vagrant/elasticsearch
tar -xvzf /tmp/elasticsearch-5.1.1.tar.gz -C /home/vagrant/elasticsearch --strip-components=1
sudo chown -R vagrant /home/vagrant/elasticsearch
sudo chgrp -R vagrant /home/vagrant/elasticsearch
sudo chown -R vagrant /home/vagrant/elasticsearch/logs
sudo chgrp -R vagrant /home/vagrant/elasticsearch/logs

# Run elasticsearch
sudo -u vagrant /home/vagrant/elasticsearch/bin/elasticsearch -d # re-run if you shutdown your computer

# Install Elasticsearch for Hadoop
curl -Lko /tmp/elasticsearch-hadoop-5.1.1.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.1.1.zip
unzip /tmp/elasticsearch-hadoop-5.1.1.zip
mv /home/vagrant/elasticsearch-hadoop-5.1.1 /home/vagrant/elasticsearch-hadoop
cp /home/vagrant/elasticsearch-hadoop/dist/elasticsearch-hadoop-5.1.1.jar /home/vagrant/Agile_Data_Code_2/lib/
cp /home/vagrant/elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.1.1.jar /home/vagrant/Agile_Data_Code_2/lib/
echo "spark.speculation false" | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf
rm -f /tmp/elasticsearch-hadoop-5.1.1.zip
rm -rf /home/vagrant/elasticsearch-hadoop/conf/spark-defaults.conf

#
# Spark jar setup
#

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
cd /home/vagrant/Agile_Data_Code_2
curl -Lko lib/snappy-java-1.1.2.6.jar http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
curl -Lko lib/lzo-hadoop-1.0.5.jar http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar
cd /home/vagrant

# Set the spark.jars path
echo "spark.jars /home/vagrant/Agile_Data_Code_2/lib/mongo-hadoop-spark-1.5.2.jar,/home/vagrant/Agile_Data_Code_2/lib/mongo-java-driver-3.4.0.jar,/home/vagrant/Agile_Data_Code_2/lib/mongo-hadoop-1.5.2.jar,/home/vagrant/Agile_Data_Code_2/lib/elasticsearch-spark-20_2.10-5.1.1.jar,/home/vagrant/Agile_Data_Code_2/lib/snappy-java-1.1.2.6.jar,/home/vagrant/Agile_Data_Code_2/lib/lzo-hadoop-1.0.5.jar" | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf

#
# Kafka install and setup
#
curl -Lko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
mkdir -p /home/vagrant/kafka
tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C /home/vagrant/kafka --strip-components=1 && rm -f /tmp/kafka_2.11-0.10.1.1.tgz

# Run zookeeper (which kafka depends on), then Kafka
/home/vagrant/kafka/bin/zookeeper-server-start.sh -daemon /home/vagrant/kafka/config/zookeeper.properties
/home/vagrant/kafka/bin/kafka-server-start.sh -daemon /home/vagrant/kafka/config/server.properties

# Give to vagrant
sudo chown -R vagrant /home/vagrant/kafka
sudo chgrp -R vagrant /home/vagrant/kafka

#
# Install and setup Airflow
#
pip install airflow
mkdir /home/vagrant/airflow
mkdir /home/vagrant/airflow/dags
mkdir /home/vagrant/airflow/logs
mkdir /home/vagrant/airflow/plugins
airflow initdb
airflow webserver -D
airflow scheduler -D

#
# Install and configure zeppelin
#
curl -Lko /tmp/zeppelin-0.6.2-bin-all.tgz http://www-us.apache.org/dist/zeppelin/zeppelin-0.6.2/zeppelin-0.6.2-bin-all.tgz
mkdir -p /home/vagrant/zeppelin
tar -xvzf /tmp/zeppelin-0.6.2-bin-all.tgz -C /home/vagrant/zeppelin --strip-components=1
rm -f /tmp/zeppelin-0.6.2-bin-all.tgz

# Configure Zeppelin
cp /home/vagrant/zeppelin/conf/zeppelin-env.sh.template /home/vagrant/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_HOME=/home/vagrant/spark" | sudo tee -a /home/vagrant/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_MASTER=local" | sudo tee -a /home/vagrant/zeppelin/conf/zeppelin-env.sh
echo "export SPARK_CLASSPATH=" | sudo tee -a /home/vagrant/zeppelin/conf/zeppelin-env.sh

# Give to vagrant
sudo chown -R vagrant /home/vagrant/zeppelin
sudo chgrp -R vagrant /home/vagrant/zeppelin

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
# Cleanup
#
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
