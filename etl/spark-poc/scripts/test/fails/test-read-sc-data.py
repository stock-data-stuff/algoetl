""" Test that Spark SQL can read a *nested* directory of JSON files """
# Note: this does not name the columns

import pyspark


def main():
    """ Program entry point """

    # Create this table
    tbl = 'stg_sc'
    # Use the JSON files found in this directory
    loc = '/var/lib/feed_history/sc'

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

        # ERROR:
        #   It is not allowed to specify partition columns when the table schema is not defined.
        #   When the table schema is not provided, schema and partition columns will be inferred
        # NOTE:
        #   If partitioning is not used, we can omit the schema; then, it will be inferred.
        # sql = "create external table if not exists " + tbl
        # sql += " using json"
        # sql += " partitioned by (api)"
        # sql += " location '" + loc + "'"

        # This reads nothing. Just get 0 rows
        #
        #sql = "create external table if not exists " + tbl
        #sql += "( date STRING, open STRING, high STRING, low STRING, close STRING, volume STRING, symbol STRING )"
        #sql += " using json"
        #sql += " partitioned by (symbol)"
        #sql += " location '" + loc + "'"
        #ssc.sql(sql)

        sql = "select * from " + tbl
        df = ssc.sql(sql)
        df.show()

        # Yes, fluent API works
        ssc.sql("select count(*) as cnt from " + tbl).show()

        # sql = "drop table " + tbl
        # ssc.sql(sql)
    print("Done")


if __name__ == "__main__":
    main()
