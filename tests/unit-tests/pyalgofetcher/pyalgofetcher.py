#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import datetime
import yaml
import pandas_datareader as web
import pandas as pd


class Pyalgofetcher:
    def __init__(self, cfg):
        """ Construct the fetcher object """
        self.config_file = cfg.config_file  # Config file
        self.history_dir = cfg.history_dir  # Output of this project
        self.feed_name = cfg.feed  # Feed(s) to run
        logging.debug("config_file = " + self.config_file)
        logging.debug("history_dir = " + self.history_dir)
        logging.debug("feed_name = " + self.feed_name)
        # Create the history_dir (if it doesn't exist). Allow it to be a symlink
        if not os.path.isdir(self.history_dir) and not os.path.islink(self.history_dir):
            os.mkdir(self.history_dir)
        # Read the config file.
        if not os.path.isfile(self.config_file):
            logging.error("Config file is missing: " + self.config_file)
            sys.exit(1)
        with open(self.config_file, "r") as yamlfile:
            self.cfg_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            logging.info("Read successful")
        logging.info(self.cfg_data)
        # start and end of processing
        # TODO: assert that the start/end date formats are 'yyyy-mm-dd'
        self.start_date = cfg.start_date
        self.end_date = cfg.end_date
        # Allow overriding the output format
        if cfg.output_format is not None:
            if cfg.output_format.lower() == 'json':
                self.output_format = 'json'
            elif cfg.output_format.lower() == 'csv':
                self.output_format = 'csv'
            else:
                logging.critical("init(): Unsupported output format parameter: " + cfg.output_format)
                sys.exit(1)
        else:
            self.output_format = self.cfg_data['output']['format']
        logging.info("Output format is:" + self.output_format)
        # Allow overriding the compression
        if cfg.compression is not None:
            if cfg.compression.lower() == 'gz':
                self.compression = 'gz'
            elif cfg.compression.lower() == 'bz2':
                self.compression = 'bz2'
            elif cfg.compression.lower() == 'xz':
                self.compression = 'xz'
            elif cfg.compression.lower() == 'zip':
                self.compression = 'zip'
            else:
                logging.critical("init(): Unsupported compression: " + cfg.compression)
                sys.exit(1)
        else:
            self.compression = self.cfg_data['output']['format_args']['compression']
        logging.info("Compression is:" + self.compression)

    def write_df(self, abs_filename, df):
        """ Write the dataframe to a file. Format details are in the config data"""
        logging.info("Writing dataframe to:" + abs_filename)
        if self.output_format == "csv":
            csv_header = self.cfg_data['output']['format_args']['header']
            if str(csv_header).lower() == 'false':
                df.to_csv(abs_filename, header=None)
            else:
                df.to_csv(abs_filename)
        elif self.output_format == "json":
            orient = self.cfg_data['output']['format_args']['orient']
            if str(orient).lower() == 'records':
                df.to_json(abs_filename, orient="records", lines=True)
            else:
                df.to_json(abs_filename)
        else:
            logging.critical("write_df(): Unsupported output format parameter: " + self.output_format)
            sys.exit(1)

    def make_rel_filename(self, feed_type, symbol):
        """ Create a filename given the feed parameters """
        rel_filename = feed_type + "_" + symbol + "_"
        rel_filename += self.start_date + "_" + self.end_date + "." + self.output_format
        # If compression is enabled, append the extension to the filename
        if self.compression is not None and self.compression.lower() != "none":
            rel_filename += "." + self.compression.replace(".", "")
        return rel_filename

    def process_pdr_feed(self, feed, feed_dir, feed_type):
        """ Process data that is read via the pandas datareader API """
        logging.info("Loading feed_type: " + feed_type + " feed:" + feed)
        args = self.cfg_data['feeds'][feed]['args']
        logging.debug("Args:" + str(args))
        symbol = args['symbol']
        source = args['source']
        start = datetime.datetime.fromisoformat(self.start_date)
        end = datetime.datetime.fromisoformat(self.end_date)
        # Fetch the data into a dataframe
        # If there is no data for the date range given, this throws a "KeyError" on 'Date'
        try:
            df = web.DataReader(symbol, source, start, end)
        except KeyError as e:
            logging.error("No data found. Got KeyError:" + str(e))
            logging.critical(
                "No data found for feed:" + feed + " for range: " + self.start_date + " to " + self.end_date)
            sys.exit(1)
        # Name the file such that we can put all files in one dir and later be able to identify its details
        rel_filename = self.make_rel_filename(feed_type, symbol)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, df)

    def process_fed_feed(self, feed, feed_dir, feed_type):
        """ Process data that is read from the New York Fed website (rest) API """
        logging.info("Loading feed_type: " + feed_type + " feed:" + feed)
        args = self.cfg_data['feeds'][feed]['args']
        logging.debug("Args:" + str(args))
        symbol = args['symbol']
        product_code = args['productCode']
        query = args['query']
        holding_types = args['holdingTypes']
        # Construct the query URL
        url = 'https://markets.newyorkfed.org/read?productCode=' + product_code
        url += '&startDt=' + self.start_date + '&endDt=' + self.end_date
        url += '&query=' + query + '&holdingTypes=' + holding_types + '&format=csv'
        # Fetch the data into a dataframe
        try:
            df = pd.read_csv(url)
        except Exception as e:
            logging.error("Failed to get data. Error:" + str(e))
            logging.critical(
                "Error while fetching data. feed:" + feed + " for range: " + self.start_date + " to " + self.end_date)
            sys.exit(1)
        # Name the file such that we can put all files in one dir and later be able to identify its details
        output_format = self.output_format
        rel_filename = self.make_rel_filename(feed_type, symbol)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, df)

    def create_feed_dir(self, feed, feed_type):
        """ Ensure the directory to hold the data for this feed exists. Return its path """
        type_dir = os.path.normpath(os.path.join(self.history_dir, feed_type))
        if os.path.isdir(type_dir):
            logging.debug("History Type directory for feed:" + feed + " exists at:" + type_dir)
        else:
            logging.debug("Creating history type directory for feed:" + feed + " at:" + type_dir)
            os.mkdir(type_dir)
        hist_dir = os.path.normpath(os.path.join(type_dir, feed))
        if os.path.isdir(hist_dir):
            logging.debug("History directory for feed:" + feed + " exists at:" + hist_dir)
        else:
            logging.debug("Creating history directory for feed:" + feed + " at:" + hist_dir)
            os.mkdir(hist_dir)
        return hist_dir

    def process_feed(self, feed):
        """ Process the given feed
        """
        feed_cfg = self.cfg_data["feeds"][feed]
        logging.debug("Feed cfg: " + str(feed_cfg))
        feed_type = feed_cfg['type']
        if feed_type == 'pdr':
            feed_dir = self.create_feed_dir(feed, feed_type)
            self.process_pdr_feed(feed, feed_dir, feed_type)
        elif feed_type == 'fed':
            feed_dir = self.create_feed_dir(feed, feed_type)
            self.process_fed_feed(feed, feed_dir, feed_type)
        else:
            logging.critical("Feed:" + feed + " has an invalid type:" + feed_type)
            sys.exit(1)

    def run(self):
        """ Run the feed loaders. If the given feed is "ALL" then load all of them.
        """
        if self.feed_name == "ALL":
            logging.info("Process all feeds")
        else:
            logging.info("Processing just feed: " + self.feed_name)
        # Process the given feed, or ALL feeds.
        feeds = self.cfg_data['feeds']
        for feed in feeds:
            logging.debug("Feed: " + str(feed))
            if feed == self.feed_name or self.feed_name == 'ALL':
                logging.debug("Processing feed with name: " + feed)
                self.process_feed(feed)
            else:
                logging.debug("Skipping feed with name: " + feed)


def read_cli_args(argv):
    """ Read the CLI args and return sane settings
    """
    # Hard-coded Defaults
    cur_dir = os.getcwd()
    log_level = "DEBUG"
    config_file = os.path.normpath(os.path.join(cur_dir, "config.yaml"))
    history_dir = os.path.normpath(os.path.join(cur_dir, "feed-history"))
    feed = 'ALL'
    start_date = '2017-01-31'
    end_date = '2018-01-31'
    output_format = None
    compression = None
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
    parser.add_argument('-o', '--output-format',
                        action='store', type=str, dest="output_format",
                        help='Output format. csv and json are supported. Default: from config file',
                        default=output_format)
    parser.add_argument('-C', '--compression',
                        action='store', type=str, dest="compression",
                        help='Compression. Default: from config file',
                        default=compression)
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
