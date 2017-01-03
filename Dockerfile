# Setup an environment for running this book's examples

FROM ubuntu
MAINTAINER Russell Jurney, russell.jurney@gmail.com

# Update apt-get
RUN apt-get update

# Things we'll need
RUN apt-get install -y zip unzip curl bzip2 python-dev build-essential

# Setup Oracle Java8
RUN apt-get install -y software-properties-common debconf-utils
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN apt-get install -y oracle-java8-installer
ENV JAVA_HOME=/usr/lib/jvm/java-8-oracle

# Download and install Anaconda Python
WORKDIR /root
ADD http://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh /tmp/Anaconda3-4.2.0-Linux-x86_64.sh
RUN bash /tmp/Anaconda3-4.2.0-Linux-x86_64.sh -b -p /root/anaconda
ENV PATH="/root/anaconda/bin:$PATH"

#
# Install git, clone repo, install Python dependencies
#
WORKDIR /root
RUN apt-get install -y git
RUN git clone https://github.com/rjurney/Agile_Data_Code_2
WORKDIR /root/Agile_Data_Code_2
ENV PROJECT_HOME=/Agile_Data_Code_2
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN bash /root/Agile_Data_Code_2/download.sh

#
# Install Hadoop: may need to update this link... see http://hadoop.apache.org/releases.html
#
WORKDIR /root
ADD http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz /tmp/hadoop-2.7.3.tar.gz
RUN mkdir -p /root/hadoop
RUN tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1
ENV HADOOP_HOME=/root/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin
ENV HADOOP_CLASSPATH=/root/hadoop/etc/hadoop/:/root/hadoop/share/hadoop/common/lib/*:/root/hadoop/share/hadoop/common/*:/root/hadoop/share/hadoop/hdfs:/root/hadoop/share/hadoop/hdfs/lib/*:/root/hadoop/share/hadoop/hdfs/*:/root/hadoop/share/hadoop/yarn/lib/*:/root/hadoop/share/hadoop/yarn/*:/root/hadoop/share/hadoop/mapreduce/lib/*:/root/hadoop/share/hadoop/mapreduce/*:/root/hadoop/etc/hadoop:/root/hadoop/share/hadoop/common/lib/*:/root/hadoop/share/hadoop/common/*:/root/hadoop/share/hadoop/hdfs:/root/hadoop/share/hadoop/hdfs/lib/*:/root/hadoop/share/hadoop/hdfs/*:/root/hadoop/share/hadoop/yarn/lib/*:/root/hadoop/share/hadoop/yarn/*:/root/hadoop/share/hadoop/mapreduce/lib/*:/root/hadoop/share/hadoop/mapreduce/*:/root/hadoop/contrib/capacity-scheduler/*.jar:/root/hadoop/contrib/capacity-scheduler/*.jar
ENV HADOOP_CONF_DIR=/root/hadoop/etc/hadoop

#
# Install Spark: may need to update this link... see http://spark.apache.org/downloads.html
#
WORKDIR /root
ADD http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz /tmp/spark-2.1.0-bin-without-hadoop.tgz
RUN mkdir -p /root/spark
RUN tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C spark --strip-components=1
ENV SPARK_HOME=/root/spark
ENV HADOOP_CONF_DIR=/root/hadoop/etc/hadoop/
ENV SPARK_DIST_CLASSPATH=/root/hadoop/etc/hadoop/:/root/hadoop/share/hadoop/common/lib/*:/root/hadoop/share/hadoop/common/*:/root/hadoop/share/hadoop/hdfs:/root/hadoop/share/hadoop/hdfs/lib/*:/root/hadoop/share/hadoop/hdfs/*:/root/hadoop/share/hadoop/yarn/lib/*:/root/hadoop/share/hadoop/yarn/*:/root/hadoop/share/hadoop/mapreduce/lib/*:/root/hadoop/share/hadoop/mapreduce/*:/root/hadoop/etc/hadoop:/root/hadoop/share/hadoop/common/lib/*:/root/hadoop/share/hadoop/common/*:/root/hadoop/share/hadoop/hdfs:/root/hadoop/share/hadoop/hdfs/lib/*:/root/hadoop/share/hadoop/hdfs/*:/root/hadoop/share/hadoop/yarn/lib/*:/root/hadoop/share/hadoop/yarn/*:/root/hadoop/share/hadoop/mapreduce/lib/*:/root/hadoop/share/hadoop/mapreduce/*:/root/hadoop/contrib/capacity-scheduler/*.jar:/root/hadoop/contrib/capacity-scheduler/*.jar
ENV PATH=$PATH:/root/spark/bin

# Have to set spark.io.compression.codec in Spark local mode, give 8GB RAM
RUN cp /root/spark/conf/spark-defaults.conf.template /root/spark/conf/spark-defaults.conf
RUN echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' >> /root/spark/conf/spark-defaults.conf
RUN echo "spark.driver.memory 8g" >> /root/spark/conf/spark-defaults.conf

# Setup spark-env.sh to use Python 3
RUN echo "PYSPARK_PYTHON=python3" >> /root/spark/conf/spark-env.sh
RUN echo "PYSPARK_DRIVER_PYTHON=python3" >> /root/spark/conf/spark-env.sh

# Setup log4j config to reduce logging output
RUN cp /root/spark/conf/log4j.properties.template /root/spark/conf/log4j.properties
RUN sed -i .bak 's/INFO/ERROR/g' /root/spark/conf/log4j.properties

#
# Install Mongo, Mongo Java driver, and mongo-hadoop
#
WORKDIR /root
ADD https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon-3.4.1.tgz /tmp/mongodb-linux-x86_64-amazon-3.4.1.tgz
RUN mkdir mongodb
RUN tar -xvf /tmp/mongodb-linux-x86_64-amazon-3.4.1.tgz -C mongodb --strip-components=1
ENV PATH=$PATH:/root/mongodb/bin
RUN mkdir -p /root/mongodb/data/db

# Start MongoDB
RUN /root/mongodb/bin/mongod --dbpath /root/mongodb/data/db

# Get the MongoDB Java Driver and put it in Agile_Data_Code_2
ADD http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.0/mongo-java-driver-3.4.0.jar /tmp/mongo-java-driver-3.4.0.jar
RUN cp /tmp/mongo-java-driver-3.4.0.jar /root/Agile_Data_Code_2/lib/

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
WORKDIR /root
ADD https://github.com/mongodb/mongo-hadoop/archive/r1.5.2.tar.gz /tmp/mongo-hadoop-r1.5.2.tar.gz
RUN mkdir -p /root/mongo-hadoop
RUN tar -xvzf /tmp/mongo-hadoop-r1.5.2.tar.gz -C mongo-hadoop --strip-components=1
WORKDIR /root/mongo-hadoop
RUN /root/mongo-hadoop/gradlew jar
WORKDIR /root
RUN cp /root/mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar /root/Agile_Data_Code_2/lib/
RUN cp /root/mongo-hadoop/build/libs/mongo-hadoop-*.jar /root/Agile_Data_Code_2/lib/

# Install pymongo_spark
WORKDIR /root/mongo-hadoop/spark/src/main/python
RUN python setup.py install
WORKDIR /root
RUN cp /root/mongo-hadoop/spark/src/main/python/pymongo_spark.py /root/Agile_Data_Code_2/lib/
ENV PYTHONPATH=$PYTHONPATH:/root/Agile_Data_Code_2/lib

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
WORKDIR /root
ADD https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.tar.gz /tmp/elasticsearch-5.1.1.tar.gz
RUN mkdir /root/elasticsearch
RUN tar -xvzf /tmp/elasticsearch-5.1.1.tar.gz -C elasticsearch --strip-components=1

# Run elasticsearch
RUN /root/elasticsearch/bin/elasticsearch

# Install Elasticsearch for Hadoop
WORKDIR /root
ADD http://download.elastic.co/hadoop/elasticsearch-hadoop-5.1.1.zip /tmp/elasticsearch-hadoop-5.1.1.zip
RUN unzip /tmp/elasticsearch-hadoop-5.1.1.zip
RUN mv /root/elasticsearch-hadoop-5.1.1 /root/elasticsearch-hadoop
RUN cp /root/elasticsearch-hadoop/dist/elasticsearch-hadoop-5.1.1.jar /root/Agile_Data_Code_2/lib/
RUN cp /root/elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.1.1.jar /root/Agile_Data_Code_2/lib/
RUN echo "spark.speculation false" >> /root/spark/conf/spark-defaults.conf

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
ADD http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar /tmp/snappy-java-1.1.2.6.jar
RUN cp /tmp/snappy-java-1.1.2.6.jar /root/Agile_Data_Code_2/lib/
ADD http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.5/lzo-hadoop-1.0.5.jar /tmp/lzo-hadoop-1.0.5.jar
RUN cp /tmp/lzo-hadoop-1.0.5.jar /root/Agile_Data_Code_2/lib/

# Setup mongo and elasticsearch jars for Spark
RUN echo "spark.jars /root/Agile_Data_Code_2/lib/mongo-hadoop-spark-1.5.2.jar,/root/Agile_Data_Code_2/lib/mongo-java-driver-3.4.0.jar,/root/Agile_Data_Code_2/lib/mongo-hadoop-1.5.2.jar,/root/Agile_Data_Code_2/lib/elasticsearch-spark-20_2.10-5.1.1.jar,/root/Agile_Data_Code_2/lib/snappy-java-1.1.2.6.jar,/root/Agile_Data_Code_2/lib/lzo-hadoop-1.0.5.jar" >> /root/spark/conf/spark-defaults.conf

#
# Install and setup Kafka
#
WORKDIR /root
ADD http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz /tmp/kafka_2.11-0.10.1.1.tgz
RUN mkdir -p /root/kafka
RUN tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C kafka --strip-components=1

# Run zookeeper (which kafka depends on), then Kafka
RUN /root/kafka/bin/zookeeper-server-start.sh /root/kafka/config/zookeeper.properties
RUN /root/kafka/bin/kafka-server-start.sh /root/kafka/config/server.properties

#
# Install and set up Airflow
#
# Install Apache Incubating Airflow
WORKDIR /root
RUN pip install airflow # should have already installed via above: pip install -r requirements.txt
RUN mkdir /root/airflow
RUN mkdir /root/airflow/dags
RUN mkdir /root/airflow/logs
RUN mkdir /root/airflow/plugins
RUN airflow initdb
RUN airflow webserver -D
RUN airflow scheduler -D

#
# Install and setup Zeppelin
#
WORKDIR /root
ADD http://www-us.apache.org/dist/zeppelin/zeppelin-0.6.2/zeppelin-0.6.2-bin-all.tgz /tmp/zeppelin-0.6.2-bin-all.tgz
RUN mkdir -p /root/zeppelin
RUN tar -xvzf /tmp/zeppelin-0.6.2-bin-all.tgz -C zeppelin --strip-components=1

# Configure Zeppelin
RUN cp /root/zeppelin/conf/zeppelin-env.sh.template /root/zeppelin/conf/zeppelin-env.sh
RUN echo "export SPARK_HOME=/root/spark" >> /root/zeppelin/conf/zeppelin-env.sh
RUN echo "export SPARK_MASTER=local" >> /root/zeppelin/conf/zeppelin-env.sh
RUN echo "export SPARK_CLASSPATH=" >> /root/zeppelin/conf/zeppelin-env.sh

# Done!