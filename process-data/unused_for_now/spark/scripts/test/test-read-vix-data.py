""" Test that Spark SQL can read a directory of JSON files """

# import pyspark
from pyspark.sql import SparkSession


def main():
    """ Program entry point """

    # Create this table
    tbl = 'stg_vix'
    # Use the JSON files found in this directory
    loc = '/feed_history/sc/vix/'

    # Initialize a spark context
    app_name = 'test-read-vix-data'

    # "CREATE TABLE" syntax requires Hive Support
    s = SparkSession.builder\
        .enableHiveSupport()\
        .appName(app_name)\
        .getOrCreate()

    sql = "drop table if exists " + tbl
    s.sql(sql)

    sql = "create table if not exists " + tbl + " using json" + " location '" + loc + "'"
    s.sql(sql)

    sql = "select * from " + tbl
    df = s.sql(sql)
    df.show()

    # Yes, fluent API works
    s.sql("select count(*) as cnt from %s" % tbl).show()

    print("Done")


if __name__ == "__main__":
    main()
