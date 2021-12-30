#!/usr/bin/env python3

import os
import sys
import argparse
import logging

# import external pandas_datareader library with alias of web
import pandas_datareader as web

# import datetime internal datetime module
# datetime is a Python module
import datetime


def load_data():
    """ Load data """
    # datetime.datetime is a data type within the datetime module
    start = datetime.datetime(1990, 1, 1)
    end = datetime.datetime(2021, 12, 18)

    # DataReader method name is case sensitive
    df = web.DataReader("VIX", 'yahoo', start, end)
    df = web.DataReader()


# invoke to_csv for df dataframe object from
    # DataReader method in the pandas_datareader library
    df.to_csv('VIX.csv')


def read_cli_args(argv):
    """ Read the CLI args and return sane settings
    """

    # Hard-coded Defaults
    cur_dir = os.getcwd()
    log_level = "DEBUG"

    config_file = os.path.normpath(os.path.join(cur_dir, "config.yaml"))
    build_dir = os.path.normpath(os.path.join(cur_dir, "build"))
    feed = 'VIX'

    # Parse the args
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level',
                        action='store', type=str, dest="log_level",
                        help='Set the logging level. Default:'
                             + log_level,
                        default=log_level)
    parser.add_argument('-c', '--config-file',
                        action='store', type=str, dest="config_file",
                        help='Path to Config file. Default:'
                             + config_file,
                        default=config_file)
    parser.add_argument('-b', '--build-dir',
                        action='store', type=str, dest="build_dir",
                        help='Path to the output diretory for this project. Default:'
                             + build_dir,
                        default=build_dir)

    args = parser.parse_args()
    return args


def configure_logging(cfg):
    """ Set up logging
    """
    log_level = cfg.log_level.upper()
    logging.basicConfig(format='%(levelname)s:%(asctime)s: %(message)s', level=log_level)
    logging.debug("Logging test DEBUG message")
    logging.info("Logging test INFO message")


def main(argv):
    app_cfg = read_cli_args(argv)
    configure_logging(app_cfg)
    load_data()


if __name__ == "__main__":
    main(sys.argv[1:])
