""" Test that Spark SQL can create a table """

import pyspark

from pyspark.sql import SQLContext


def main():
    """ Program entry point """

    # Intialize a spark context
    app_name = 'feed-history-ddl'
    spark_cluster = "local"
    with pyspark.SparkContext(spark_cluster, app_name) as spark_context:
        s = SQLContext(spark_context)
        s.sql("drop table if exists test_table")
        s.sql("create table if not exists test_table(i int,s string)")
        s.sql("insert into test_table values(1, 'one')")
        s.sql("insert into test_table values(6, 'six')")
        df = s.sql("select * from test_table")
        df.show()
    print("Done")


if __name__ == "__main__":
    main()
