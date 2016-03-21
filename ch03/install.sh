#!/usr/bin/env bash
#
# This file is intended as a guide to installation, and not a complete script that will work on all platforms. Use accordingly. I think it works, though.
#

export PROJECT_HOME=`pwd`"/.."

if [ "$(uname)" == "Darwin" ]; then
    ANADONCA_OS_NAME='MacOSX'      
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    ANADONCA_OS_NAME='Linux'
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    ANADONCA_OS_NAME='Windows'
fi

# Download and install Anaconda
wget -P /tmp/ "http://repo.continuum.io/archive/Anaconda2-2.5.0-${ANADONCA_OS_NAME}-x86_64.sh"
bash "/tmp/Anaconda2-2.5.0-${ANADONCA_OS_NAME}-x86_64.sh" -b -p $HOME/anaconda
export PATH="$HOME/anaconda/bin:$PATH"
echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile

#
# Install Hadoop in the hadoop directory in the root of our project. Also, setup
# our Hadoop environment for Spark to run
#
wget -P /tmp/ http://apache.osuosl.org/hadoop/common/hadoop-2.6.4/hadoop-2.6.4.tar.gz

cd ..

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

cd ch03

#
# Install Spark in the spark directory in the root of our project. Also, setup
# our Spark environment for PySpark to run
#

# May need to update this link... see http://spark.apache.org/downloads.html
wget -P /tmp/ http://d3kbcqa49mib13.cloudfront.net/spark-1.6.1-bin-without-hadoop.tgz
cd ..
mkdir spark
tar -xvf /tmp/spark-1.6.1-bin-without-hadoop.tgz -C spark --strip-components=1
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
cp ../spark/conf/spark-defaults.conf.template ../spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.LZ4CompressionCodec' >> ../spark/conf/spark-defaults.conf

cd ch03

