""" Test that Spark SQL can create a table """

# import pyspark
from pyspark.sql import SparkSession


def main():
    """ Program entry point """

    app_name = 'test-spark-sql'

    # "CREATE TABLE" syntax requires Hive Support
    s = SparkSession.builder\
        .enableHiveSupport()\
        .appName(app_name)\
        .getOrCreate()

    s.sql("drop table if exists test_table")
    s.sql("create table if not exists test_table(i int,s string)")
    s.sql("insert into test_table values(1, 'one')")
    s.sql("insert into test_table values(6, 'six')")
    df = s.sql("select * from test_table")
    df.show()
    print("Done")


if __name__ == "__main__":
    main()
