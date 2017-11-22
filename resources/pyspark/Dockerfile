FROM frolvlad/alpine-oraclejdk8:8.151.12-cleaned

RUN apk add --update \
    wget \
    python \
    python-dev \
    py-pip \
    nano \
    bash

RUN pip install pymongo

ENV LANG=C.UTF-8
ENV HOME /opt
ENV SPARK_VERSION 2.2.0
ENV HADOOP_VERSION 2.7
ENV MONGO_SPARK_VERSION 2.2.0
ENV SCALA_VERSION 2.10

WORKDIR ${HOME}

ENV SPARK_HOME ${HOME}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

ENV PATH $PATH:${SPARK_HOME}/bin

# Get Spark
RUN wget http://ftp.tudelft.nl/apache/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
tar xvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN rm -fv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Create a Spark config file and add the Mongo-Spark connector as dependency
RUN cp ${SPARK_HOME}/conf/spark-defaults.conf.template ${SPARK_HOME}/conf/spark-defaults.conf
RUN echo "spark.jars.packages org.mongodb.spark:mongo-spark-connector_${SCALA_VERSION}:${MONGO_SPARK_VERSION}" >> ${SPARK_HOME}/conf/spark-defaults.conf
