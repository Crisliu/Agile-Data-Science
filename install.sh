#!/usr/bin/env bash
#
# This file is intended as a guide to installation, and not a complete script that will work on all platforms. Use accordingly. I think it works, though.
#

export PROJECT_HOME=`pwd`
echo "export PROJECT_HOME=$PROJECT_HOME" >> ~/.bash_profile

if [ "$(uname)" == "Darwin" ]; then
    ANADONCA_OS_NAME='MacOSX'
    MONGO_DOWNLOAD_URL='https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.2.4.tgz'
    MONGO_FILE=''
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    ANADONCA_OS_NAME='Linux'
    MONGO_DOWNLOAD_URL='https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon-3.2.4.tgz'
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    ANADONCA_OS_NAME='Windows'
    MONGO_DOWNLOAD_URL='https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-3.2.4-signed.msi'
fi

# Download and install Anaconda
wget -P /tmp/ "http://repo.continuum.io/archive/Anaconda3-4.2.0-${ANADONCA_OS_NAME}-x86_64.sh"
bash "/tmp/Anaconda3-4.2.0-${ANADONCA_OS_NAME}-x86_64.sh" -b -p $HOME/anaconda
export PATH="$HOME/anaconda/bin:$PATH"
echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile

#
# Install Hadoop in the hadoop directory in the root of our project. Also, setup
# our Hadoop environment for Spark to run
#
wget -P /tmp/ http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz

mkdir hadoop
tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1
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
# Install Spark in the spark directory in the root of our project. Also, setup
# our Spark environment for PySpark to run
#

# May need to update this link... see http://spark.apache.org/downloads.html
wget -P /tmp/ http://d3kbcqa49mib13.cloudfront.net/spark-2.0.2-bin-without-hadoop.tgz

mkdir spark
tar -xvf /tmp/spark-2.0.2-bin-without-hadoop.tgz -C spark --strip-components=1
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
cp spark/conf/spark-defaults.conf.template spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' >> spark/conf/spark-defaults.conf

# Give Spark 6GB of RAM
echo "spark.driver.memory 8g" >> $SPARK_HOME/conf/spark-defaults.conf

echo "PYSPARK_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh
echo "PYSPARK_DRIVER_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh

#
# Install MongoDB in the mongo directory in the root of our project. Also, get the jar for the MongoDB driver
# and the mongo-hadoop project.
#

wget -P /tmp/ $MONGO_DOWNLOAD_URL
MONGO_FILE_NAME=${MONGO_DOWNLOAD_URL##*/}
mkdir mongodb
tar -xvf /tmp/$MONGO_FILE_NAME -C mongodb --strip-components=1
export PATH=$PATH:$PROJECT_HOME/mongodb/bin
echo 'export PATH=$PATH:$PROJECT_HOME/mongodb/bin' >> ~/.bash_profile
mkdir -p mongodb/data/db

# Start Mongo
mongodb/bin/mongod --dbpath mongodb/data/db & # re-run if you shutdown your computer

# Get the MongoDB Java Driver
wget -P lib/ http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.0/mongo-java-driver-3.4.0.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
wget -P /tmp/ https://github.com/mongodb/mongo-hadoop/archive/r1.5.2.tar.gz
mkdir mongo-hadoop
tar -xvzf /tmp/r1.5.2.tar.gz -C mongo-hadoop --strip-components=1

# Now build the mongo-hadoop-spark jars
cd mongo-hadoop
./gradlew jar
cd ..
cp mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar lib/
cp mongo-hadoop/build/libs/mongo-hadoop-*.jar lib/

# Now build the pymongo_spark package
# pip install py4j # add sudo if needed
# pip install pymongo # add sudo if needed
# pip install pymongo-spark # add sudo if needed
cd mongo-hadoop/spark/src/main/python
python setup.py install
cd $PROJECT_HOME# to $PROJECT_HOME
cp mongo-hadoop/spark/src/main/python/pymongo_spark.py lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' >> ~/.bash_profile

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
wget -P /tmp/ https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.3.5/elasticsearch-2.3.5.tar.gz
mkdir elasticsearch
tar -xvzf /tmp/elasticsearch-2.3.5.tar.gz -C elasticsearch --strip-components=1

# Run elasticsearch
elasticsearch/bin/elasticsearch 2>1 > /dev/null & # re-run if you shutdown your computer

# Install Elasticsearch for Hadoop
wget -P /tmp/ http://download.elastic.co/hadoop/elasticsearch-hadoop-5.0.0-alpha5.zip
unzip /tmp/elasticsearch-hadoop-5.0.0-alpha5.zip
mv elasticsearch-hadoop-5.0.0-alpha5 elasticsearch-hadoop
cp elasticsearch-hadoop/dist/elasticsearch-hadoop-5.0.0-alpha5.jar lib/
cp elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.0.0-alpha5.jar lib/
echo "spark.speculation false" >> $PROJECT_HOME/spark/conf/spark-defaults.conf

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
wget -P lib/ http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
wget -P lib/ http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar

# Setup mongo and elasticsearch jars for Spark
echo "spark.jars $PROJECT_HOME/lib/mongo-hadoop-spark-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/mongo-java-driver-3.2.2.jar,\
$PROJECT_HOME/lib/mongo-hadoop-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/elasticsearch-spark-20_2.10-5.0.0-alpha5.jar,\
$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar,\
$PROJECT_HOME/lib/lzo-hadoop-1.0.0.jar" \
  >> spark/conf/spark-defaults.conf

# Setup spark classpath for snappy for parquet
# echo "SPARK_CLASSPATH=$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar" >> spark/conf/spark-env.sh

# Install pyelasticsearch and p
# pip install pyelasticsearch

# Install Apache Kafka
wget -P /tmp/ http://www-us.apache.org/dist/kafka/0.10.1.0/kafka_2.11-0.10.1.0.tgz
mkdir kafka
tar -xvzf /tmp/kafka_2.11-0.10.1.0.tgz -C kafka --strip-components=1

# Install Apache Incubating Airflow
pip install airflow
mkdir ~/airflow/dags
mkdir ~/airflow/logs
mkdir ~/airflow/plugins
airflow initdb
airflow webserver -D

# Get bootstrap
mkdir ch03/web/static
cd ch03/web/static
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css'
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js'
wget 'http://d3js.org/d3.v3.min.js'
cd $PROJECT_HOME

# Install Apache Zeppelin
wget -P /tmp/ http://www-us.apache.org/dist/zeppelin/zeppelin-0.6.2/zeppelin-0.6.2-bin-all.tgz
mkdir zeppelin
tar -xvzf /tmp/zeppelin-0.6.2-bin-all.tgz -C zeppelin --strip-components=1

# Configure Zeppelin
cp zeppelin/conf/zeppelin-env.sh.template zeppelin/conf/zeppelin-env.sh
echo "export SPARK_HOME=$PROJECT_HOME/spark" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_MASTER=local" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_CLASSPATH=" >> zeppelin/conf/zeppelin-env.sh
