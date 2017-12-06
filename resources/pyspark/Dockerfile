FROM frolvlad/alpine-oraclejdk8:8.151.12-cleaned

RUN apk add --update \
    wget \
    python3 \
    nano \
    bash

RUN /usr/bin/pip3 install pymongo

ENV LANG=C.UTF-8
ENV HOME /opt
ENV SPARK_VERSION 2.2.0
ENV HADOOP_VERSION 2.7
ENV MONGO_SPARK_VERSION 2.2.0
ENV SCALA_VERSION 2.10
ENV PYSPARK_PYTHON /usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON /usr/bin/python3

WORKDIR ${HOME}

ENV SPARK_HOME ${HOME}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

ENV PATH $PATH:${SPARK_HOME}/bin

# Get Spark
RUN wget http://ftp.tudelft.nl/apache/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
tar xvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
RUN rm -fv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Create a Spark config file and add the Mongo-Spark connector as dependency
RUN cp ${SPARK_HOME}/conf/spark-defaults.conf.template ${SPARK_HOME}/conf/spark-defaults.conf
RUN echo "spark.master spark://master:7077" >> ${SPARK_HOME}/conf/spark-defaults.conf
RUN echo "spark.driver.memory 2g" >> ${SPARK_HOME}/conf/spark-defaults.conf
RUN echo "spark.executor.memory 2g" >> ${SPARK_HOME}/conf/spark-defaults.conf
RUN echo "spark.jars.packages org.mongodb.spark:mongo-spark-connector_${SCALA_VERSION}:${MONGO_SPARK_VERSION}" >> ${SPARK_HOME}/conf/spark-defaults.conf

WORKDIR $SPARK_HOME
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]