""" Test: Connecting directly to Postgresql, and integration with Spark """

# import psycopg2
import pandas as pd
from pyspark.sql import SparkSession
from sqlalchemy import create_engine
import logging


def get_pg_data_as_pdf(db_user, db_password, db_name):
    """ Get the data we want as a Pandas DataFrame """
    # This reads the data from Postgresql using SqlAlchemy
    conn_str = 'postgresql://' + db_user + ':' + db_password \
               + '@localhost:5432/' + db_name \
               + '?client_encoding=utf8'
    engine = create_engine(conn_str)
    pdf = pd.read_sql('select * from testschema.test_util', engine)
    return pdf


def convert_pdf_to_df(pdf, app_name, master):
    """ Given a Pandas DataFrame, return a Spark DataFrame and show it"""
    spark = SparkSession.builder.master(master).appName(app_name).getOrCreate()
    # Convert Pandas dataframe to spark DataFrame
    df = spark.createDataFrame(pdf)
    print(df.schema)
    df.show()
    return df


a_pdf = get_pg_data_as_pdf('test', 'test', 'test')
a_df = convert_pdf_to_df(a_pdf, "pyspark-postgresql-via-sqlalchemy", "local")
logging.info("Done")


