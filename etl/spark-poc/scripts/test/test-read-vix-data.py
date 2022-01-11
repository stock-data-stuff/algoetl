""" Test that Spark SQL can read a directory of JSON files """
# Note: this does not name the columns

import pyspark


def main():
    """ Program entry point """

    # Create this table
    tbl = 'stg_vix'
    # Use the JSON files found in this directory
    loc = '/var/lib/feed_history/sc/VIX_from_sc/'

    # Initialize a spark context
    app_name = 'feed-history-ddl'
    spark_cluster = "local"
    with pyspark.SparkContext(spark_cluster, app_name) as sc:
        # Create the Spark SQL Context
        ssc = pyspark.sql.SQLContext(sc)
        # For local dev in spark shell
        # ssc = SparkSession.builder.getOrCreate()

        sql = "drop table if exists " + tbl
        ssc.sql(sql)

        sql = "create table if not exists " + tbl + " using json" + " location '" + loc + "'"
        ssc.sql(sql)

        sql = "select * from " + tbl
        df = ssc.sql(sql)
        df.show()

        # Yes, fluent API works
        ssc.sql("select count(*) as cnt from stg_vix").show()

        # sql = "drop table " + tbl
        # ssc.sql(sql)
    print("Done")


if __name__ == "__main__":
    main()
