# GOAL

Document things done for local development.

# Docker Containers

## View Spark jobs

xdg-open http://localhost:8080

## PySpark

pyspark scripts on the master run using a
Spark Context with "master = local[*]"

The Spark version is 3.2.0

## JAVA

The Spark containers use OpenJDK version 8



# Local Setup

## JAVA

sudo apt install openjdk-8-jdk

# Spark



## [OPTIONAL] Get and run Spark locally

https://spark.apache.org/downloads.html
wget https://dlcdn.apache.org/spark/spark-3.2.0/spark-3.2.0-bin-hadoop3.2.tgz

Expand this and run
./spark-3.2.0-bin-hadoop3.2/bin/pyspark

## Test local Spark

import pyspark
from pyspark.sql import SQLContext
s = SparkSession.builder.getOrCreate()
s.sql('select 123').show()

