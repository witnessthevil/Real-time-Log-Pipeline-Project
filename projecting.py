import pyspark 
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,from_json,explode,split,regexp_extract
from pyspark.sql.types import StringType, StructField, StructType
import os
packages = ['org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0','org.elasticsearch:elasticsearch-spark-30_2.12:8.4.2']

spark = SparkSession.builder.appName('thisisnotyourtimetoshine').config("spark.jars.packages", ",".join(packages)).getOrCreate()

df = spark.readStream.format('kafka').option('kafka.bootstrap.servers','localhost:9092')\
    .option('subscribe','testing5')\
    .option('startingOffsets','earliest')\
    .option("failOnDataLoss","false")\
    .load()

schema = StructType([StructField('schema',StructType([StructField('type',StringType()),StructField('optional',StringType())])),StructField('payload',StringType())])


value_df = df.select(from_json(col('value').cast('string'),schema).alias('new_value'))

explode_df = value_df.selectExpr('new_value.payload')

host_pattern = r'(\d+\.+\d+\.+\d+\.+\d)\s'
date_pattern = r'(\d{2}\/\S+)\s'
time_pattern = r'(\d{2}\:\d{2}\:\d{2})'
website_pattern = r'\"\S+\s\/(\S+|)'
status_pattern = r'\s(\d{3})\s'

regex_df = explode_df.select(regexp_extract('payload',host_pattern,1).alias("Host"),
                             regexp_extract('payload',date_pattern,1).alias("Date"),
                             regexp_extract('payload',time_pattern,1).alias("Time"),
                             regexp_extract('payload',website_pattern,1).alias("Site"),
                             regexp_extract('payload',status_pattern,1).alias("Status"))

count_df = regex_df.groupBy("Site").count()


df1 = regex_df.writeStream\
.format("org.elasticsearch.spark.sql") \
.option('es.nodes.wan.only','true')\
.option("checkpointLocation", "chk-point-dir2") \
.option('es.resource', 'product/')\
.option("es.nodes", "localhost") \
.option('es.port','9200')\
.outputMode('append')\
.start()


df2 = count_df.writeStream.format('console')\
    .option('checkpointLocation','chk-point-dir3')\
    .outputMode('complete')\
    .start()

spark.streams.awaitAnyTermination()
