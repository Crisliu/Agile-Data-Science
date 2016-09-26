#!/usr/bin/env bash
#
# This file is intended as a guide to installation, and not a complete script that will work on all platforms. Use accordingly. I think it works, though.
#

export PROJECT_HOME=`pwd`"/.."

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
wget -P /tmp/ "http://repo.continuum.io/archive/Anaconda2-4.1.1-${ANADONCA_OS_NAME}-x86_64.sh"
bash "/tmp/Anaconda2-4.1.1-${ANADONCA_OS_NAME}-x86_64.sh" -b -p $HOME/anaconda
export PATH="$HOME/anaconda/bin:$PATH"
echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile

#
# Install Hadoop in the hadoop directory in the root of our project. Also, setup
# our Hadoop environment for Spark to run
#
wget -P /tmp/ http://apache.osuosl.org/hadoop/common/hadoop-2.6.4/hadoop-2.6.4.tar.gz

mkdir hadoop
tar -xvf /tmp/hadoop-2.6.4.tar.gz -C hadoop --strip-components=1
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
wget -P /tmp/ http://d3kbcqa49mib13.cloudfront.net/spark-2.0.0-bin-without-hadoop.tgz

mkdir spark
tar -xvf /tmp/spark-2.0.0-bin-without-hadoop.tgz -C spark --strip-components=1
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
echo 'spark.io.compression.codec org.apache.spark.io.LZ4CompressionCodec' >> spark/conf/spark-defaults.conf

# Give Spark 6GB of RAM
echo "spark.driver.memory 6g" >> spark/conf/spark-defaults.conf

# Install and add snappy-java to our classpath
wget -P lib/ http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
export SPARK_CLASSPATH=$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar:$SPARK_CLASSPATH
echo 'export SPARK_CLASSPATH=$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar:$SPARK_CLASSPATH' >> ~/.bash_profile

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
wget -P lib/ http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.2.2/mongo-java-driver-3.2.2.jar

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

# Setup mongo and elasticsearch jars for Spark
echo "spark.jars $PROJECT_HOME/lib/mongo-hadoop-spark-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/mongo-java-driver-3.2.2.jar,\
$PROJECT_HOME/lib/mongo-hadoop-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/elasticsearch-spark-20_2.10-5.0.0-alpha5.jar" \
  >> spark/conf/spark-defaults.conf

# Install pyelasticsearch and p
# pip install pyelasticsearch

# Get bootstrap
mkdir ch03/web/static
cd ch03/web/static
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css'
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css'
wget 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js'
wget 'http://d3js.org/d3.v3.min.js'
cd $PROJECT_HOME
