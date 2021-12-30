#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import yaml
import datetime
import pandas_datareader as web


class Pyalgofetcher:
    def __init__(self, cfg):
        # Arguments
        self.config_file = cfg.config_file  # Config file
        self.history_dir = cfg.history_dir  # Output of this project
        self.feed_name = cfg.feed  # Feed(s) to run
        logging.debug("config_file = " + self.config_file)
        logging.debug("history_dir = " + self.history_dir)
        logging.debug("feed_name = " + self.feed_name)
        # Create the history_dir (if it doesn't exist)
        if not os.path.isdir(self.history_dir):
            os.mkdir(self.history_dir)
        # Read the config file. It should be in the dir as this script
        if not os.path.isfile(self.config_file):
            logging.error("Config file is missing: " + self.config_file)
            sys.exit(1)
        with open(self.config_file, "r") as yamlfile:
            self.cfg_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            logging.info("Read successful")
        logging.info(self.cfg_data)
        # start and end of processing
        self.start_date = cfg.start_date
        self.end_date = cfg.end_date


    def process_pandas_datareader_feed(self, feed):
        # Ensure the directory to hold the data for this feed exists
        type_dir = os.path.normpath(os.path.join(self.history_dir, "pandas_datareader"))
        if os.path.isdir(type_dir):
            logging.debug("History Type directory for feed:" + feed + " exists at:" + type_dir)
        else:
            logging.debug("Creating history type directory for feed:" + feed + " at:" + type_dir)
            os.mkdir(type_dir)
        #
        hist_dir = os.path.normpath(os.path.join(type_dir, feed))
        if os.path.isdir(hist_dir):
            logging.debug("History directory for feed:" + feed + " exists at:" + hist_dir)
        else:
            logging.debug("Creating history directory for feed:" + feed + " at:" + hist_dir)
            os.mkdir(hist_dir)

        logging.info("Loading pandas_datareader type feed:" + feed)
        args = self.cfg_data['feeds'][feed]['args']
        logging.debug("Args:" + str(args))
        source = args['source']
        symbol = args['symbol']

        # datetime.datetime is a data type within the datetime module
        #start = datetime.datetime(1990, 1, 1)
        #start = datetime.datetime(2020, 12, 1) # fails since no data
        #end = datetime.datetime(2021, 12, 18)
        #
        # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
        #start = datetime.datetime.fromisoformat('1990-01-01')
        #end = datetime.datetime.fromisoformat('2021-12-18')
        start = datetime.datetime.fromisoformat(self.start_date)
        end = datetime.datetime.fromisoformat(self.end_date)

        # If there is no data for the date range given, this throws a "KeyError" on 'Date'
        try:
            df = web.DataReader(symbol, source, start, end)
        except KeyError as e:
            logging.error("No data found. Got KeyError:" + str(e))
            logging.critical("No data found for feed:" + feed + " for range: " + self.start_date + " to " + self.end_date)
            sys.exit(1)

        rel_filename = "pandas_datareader_" + source + "_" + symbol + "_" + self.start_date + "_" + self.end_date + ".csv"
        abs_filename = os.path.normpath(os.path.join(hist_dir, rel_filename))
        logging.info("Writing data to:" + abs_filename)
        df.to_csv(abs_filename)

    def process_feed(self, feed):
        """ Process the given feed
        """
        feed_cfg = self.cfg_data["feeds"][feed]
        logging.debug("Feed cfg: " + str(feed_cfg))
        feed_type = feed_cfg['type']
        if feed_type == 'pandas_datareader':
            self.process_pandas_datareader_feed(feed)
        else:
            logging.info("Feed:" + feed + " has an invalid type:" + feed_type)

    def run(self):
        """ Run the feed loaders. If the given feed is "ALL" then load all of them.
        """
        if self.feed_name == "ALL":
            logging.info("Process all feeds")
        else:
            logging.info("Processing just feed: " + self.feed_name)

        feeds = self.cfg_data['feeds']
        logging.debug("Feeds: " + str(feeds))
        for feed in feeds:
            logging.debug("Feed: " + str(feed))
            if feed == self.feed_name or self.feed_name == 'ALL':
                logging.debug("Processing feed with name: " + feed)
                self.process_feed(feed)


def read_cli_args(argv):
    """ Read the CLI args and return sane settings
    """

    # Hard-coded Defaults
    cur_dir = os.getcwd()
    log_level = "DEBUG"
    config_file = os.path.normpath(os.path.join(cur_dir, "config.yaml"))
    history_dir = os.path.normpath(os.path.join(cur_dir, "feed-history"))
    feed = 'ALL'
    start_date='1990-01-01'
    end_date='2030-01-01'

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
    parser.add_argument('-f', '--feed',
                        action='store', type=str, dest="feed",
                        help='Feed to execute. Default:' + feed,
                        default=feed)
    parser.add_argument('-d', '--history-dir',
                        action='store', type=str, dest="history_dir",
                        help='Path to the output directory for this project. Default:'
                             + history_dir,
                        default=history_dir)
    parser.add_argument('-s', '--start-date',
                        action='store', type=str, dest="start_date",
                        help='Start date to fetch data. Default:'
                             + start_date,
                        default=start_date)
    parser.add_argument('-e', '--end-date',
                        action='store', type=str, dest="end_date",
                        help='End date to fetch data. Default:'
                             + end_date,
                        default=end_date)

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
    app = Pyalgofetcher(app_cfg)
    app.run()


if __name__ == "__main__":
    main(sys.argv[1:])
