#!/usr/bin/env python3
""" This program reads the available data into stage tables for processing """

import os
import glob
import sys
import argparse
import logging
from pathlib import Path
import yaml
import pandas as pd
from sqlalchemy import create_engine


class Dataloader:
    """ This class is used to load the data to stage tables """

    def __init__(self, cfg):
        """ Construct the data loader """

        # Read the config file.
        self.config_file = cfg.config_file
        self.override_file = cfg.override_file
        self.merged_file = cfg.merged_file
        logging.debug("config_file = %s", self.config_file)
        logging.debug("override_file = %s", self.override_file)
        logging.debug("merged_file = %s", self.merged_file)
        self.config_data = self.read_config_data()

        self.history_dir = cfg.history_dir
        logging.debug("history_dir = %s", self.history_dir)

        if not os.path.exists(self.history_dir):
            logging.error("Feed history directory is missing :%s",
                          self.history_dir)

        # Database connection
        self.sqlalchemy_engine = None
        db_cfg = self.config_data['credentials']['database']
        db_type = db_cfg['db_type']
        if db_type == 'postgresql':
            logging.info("Connecting to postgresql")
            args = db_cfg['postgresql_args']
            db_host = args['db_host']
            db_port = args['db_port']
            db_user = args['db_user']
            db_password = args['db_password']
            db_database_name = args['db_database_name']
            conn_str = 'postgresql://' + db_user \
                       + ':' + str(db_password) \
                       + '@' + str(db_host) \
                       + ':' + str(db_port) \
                       + '/' + db_database_name \
                       + '?client_encoding=utf8'
            engine = create_engine(conn_str)
            self.sqlalchemy_engine = engine
            #
            # Schemas. # Used in full/3-part table name
            self.schema_stage = args['schema_stage']
            self.schema_production = args['schema_production']
            self.schema_report = args['schema_report']
        if self.sqlalchemy_engine is None:
            logging.error("Database connection failed")
            sys.exit(1)

        # Initialize schemas
        for schema in [self.schema_stage, self.schema_production, self.schema_report]:
            sql = "CREATE SCHEMA IF NOT EXISTS %s" %  schema
            self.sqlalchemy_engine.execute(sql)

        # Build up this list as we read in stage tables
        self.feed_tables = []

    def read_config_data(self):
        """ Read the configuration and override files """

        if os.path.isfile(self.config_file):
            logging.debug("Using Config file: %s", self.config_file)
            with open(self.config_file, 'r', encoding="utf8") as stream:
                try:
                    orig_config_data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    logging.critical(exc)
        else:
            logging.critical("Config file does not exist: %s", self.config_file)
            sys.exit(1)

        # Read override file if it exists
        override_file_data = {}
        if os.path.isfile(self.override_file):
            with open(self.override_file, 'r', encoding="utf8") as stream:
                try:
                    override_file_data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    logging.critical(exc)

        # Store the (merged) config data in self.config_data
        config_data = orig_config_data

        logging.debug("Applying override_file_data: %s", override_file_data)
        if override_file_data is not None:
            config_data = merge_dicts(orig_config_data, override_file_data)

        # Store the resulting merged data to a file (if given a 'merged_file')
        # This is for debugging. So the user can see the effective config data easily.
        if self.merged_file is not None:
            # Ensure parent directory for merged file exists
            directory = Path(self.merged_file).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
            # Write merged file
            with open(self.merged_file, 'w', encoding="utf8") as out_file:
                yaml.dump(config_data, out_file)

        return config_data

    def write_df(self, abs_filename, data_frame):
        """ Write the dataframe to a file. Format details are in the config data"""
        logging.info("Writing dataframe to file: %s", abs_filename)
        if data_frame is None:
            logging.warning("Dataframe is None. Exiting")
            return
        rowcount = data_frame.values.size
        if rowcount == 0:
            logging.warning("Dataframe has no rows")
            return
        logging.info("Writing dataframe with rowcount: %s to file: %s",
                     rowcount, abs_filename)
        if self.output_format == "csv":
            csv_header = self.config_data['output_config']['file']['format_args']['header']
            if str(csv_header).lower() == 'false':
                data_frame.to_csv(abs_filename, header=None, index=False,
                                  date_format='%Y-%m-%d')
            else:
                data_frame.to_csv(abs_filename, index=False,
                                  date_format='%Y-%m-%d')
        elif self.output_format == "json":
            orient = self.config_data['output_config']['file']['format_args']['orient']
            if str(orient).lower() == 'table':
                data_frame.to_json(abs_filename, orient="table",
                                   date_format='iso', date_unit='s')
            if str(orient).lower() == 'records':
                data_frame.to_json(abs_filename, orient="records", lines=True,
                                   date_format='iso', date_unit='s')
            else:
                logging.critical("Unsupported value of orient: %s", orient)
                sys.exit(1)
        else:
            logging.critical("write_df(): Unsupported output format parameter: %s",
                             self.output_format)
            sys.exit(1)

    def get_pdf_from_json_dir(self, json_dir):
        """ Return a Pandas Data Frame using all JSON files in the given dir """
        file_list = [x for x in os.listdir(json_dir) if x.endswith("json")]
        dfs = []  # an empty list to store the data frames
        for rel_filename in file_list:
            abs_filename = os.path.join(json_dir, rel_filename)
            data = pd.read_json(abs_filename, lines=True)  # read data frame from json file
            dfs.append(data)  # append the data frame to the list
        pdf = pd.concat(dfs, ignore_index=True)  # concatenate all the data frames in the list.
        logging.debug("DataFrame size: %d", pdf.size)
        return pdf

    def recreate_db_table_from_pdf(self, pdf, table_name, schema_name):
        """ Create a database table from the given Pandas DataFrame """
        sql = "DROP TABLE IF EXISTS {0}.{1}".\
            format(schema_name, table_name)
        self.sqlalchemy_engine.execute(sql)

        logging.debug("Create DB table: %s", table_name)
        pdf.to_sql(table_name, self.sqlalchemy_engine, schema=schema_name)

    def create_table_from_feed_dir(self, feed_dir, table_name, schema_name):
        """ Process the files in the feed dir
         feed_dir:
           Path to a directory of JSON files to process
         table_name:
           Name of the table to create
        """
        logging.info("Processing feed_dir=%s, table_name=%s, schema_name=%s",
                     feed_dir, table_name, schema_name)
        pdf = self.get_pdf_from_json_dir(feed_dir)
        self.recreate_db_table_from_pdf(pdf, table_name, schema_name)
        self.feed_tables.append(table_name)  # Remember the table names so we can unite them later

    def run(self):
        """ Main loop for the code """
        # Loop through the different APIs in the feed history folder
        glob_pattern = os.path.join(self.history_dir, '*')
        api_dirs = glob.glob(glob_pattern)
        for api_dir in api_dirs:
            # Infer the API from the dir
            api = os.path.basename(api_dir).lower()
            if os.path.isdir(api_dir):
                logging.debug("Found API dir: %s", api_dir)
                feed_dir_pattern = os.path.join(api_dir, '*')
                feed_dirs = glob.glob(feed_dir_pattern)
                for feed_dir in feed_dirs:
                    logging.debug("Found feed dir: %s", feed_dir)
                    # Infer the Symbol from the dir
                    table_name = os.path.basename(feed_dir).lower()
                    self.create_table_from_feed_dir(feed_dir, table_name, self.schema_stage)
        # Write the table to a (CSV) file for Excel
        # self.write_df()
        logging.info("Successfully terminating program")


def merge_dicts(dict_a, dict_b, path=None, update=True):
    """ Merge dictionary 'b' into dictionary 'a' """
    if path is None:
        path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge_dicts(dict_a[key], dict_b[key], path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass  # same leaf value
            elif isinstance(dict_a[key], list) and isinstance(dict_b[key], list):
                for idx in enumerate(dict_b[key]):
                    dict_a[key][idx] = merge_dicts(dict_a[key][idx],
                                                   dict_b[key][idx],
                                                   path + [str(key), str(idx)],
                                                   update=update)
            elif update:
                dict_a[key] = dict_b[key]
            else:
                msg = 'Conflict at %s', (path + [str(key)])
                raise Exception(msg)
        else:
            dict_a[key] = dict_b[key]
    return dict_a


def read_cli_args():
    """ Read the CLI args and return sane settings
    """
    # Hard-coded Defaults
    log_level = "DEBUG"
    # Config file
    cur_dir = os.getcwd()
    config_file = os.path.normpath(os.path.join(cur_dir,
                                                "..", "..", "..", "config.yaml"))
    override_file = os.path.normpath(os.path.join(cur_dir,
                                                  "..", "..", "..", "overrides.yaml"))
    merged_file = os.path.normpath(os.path.join(cur_dir,
                                                "..", "..", "..", ".effective-config.yaml"))
    # App specific
    history_dir = os.path.normpath(os.path.join(cur_dir,
                                                "..", "..", "..", "feed-history"))
    # Parse the args
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level',
                        action='store', type=str, dest="log_level",
                        help='Set the logging level. Default:'
                             + log_level,
                        default=log_level)
    # Config data
    parser.add_argument('-c', '--config-file',
                        action='store', type=str, dest="config_file",
                        help='Path to Config file. Default:'
                             + config_file,
                        default=config_file)
    parser.add_argument('-o', '--override-file',
                        action='store', type=str, dest="override_file",
                        help='Path to override file. Default:'
                             + override_file,
                        default=override_file)
    parser.add_argument('-m', '--merged-file',
                        action='store', type=str, dest="merged_file",
                        help='Path to output of this script. Default:'
                             + merged_file,
                        default=merged_file)
    # Main app
    parser.add_argument('-d', '--history-dir',
                        action='store', type=str, dest="history_dir",
                        help='Path to the output directory for this project. Default:'
                             + history_dir,
                        default=history_dir)
    args = parser.parse_args()
    return args


def configure_logging(cfg):
    """ Set up logging """
    log_level = cfg.log_level.upper()
    logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s', level=log_level)
    logging.debug("Logging test DEBUG message")
    logging.info("Logging test INFO message")


def main():
    """ Main program """
    print("WTF")
    app_cfg = read_cli_args()
    configure_logging(app_cfg)
    app = Dataloader(app_cfg)
    app.run()


if __name__ == "__main__":
    main()
