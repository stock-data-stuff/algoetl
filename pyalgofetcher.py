#!/usr/bin/env python3
""" This program fetches some data, as defined by the given config file."""

import os
import sys
import argparse
import logging
import datetime
from pathlib import Path
import yaml
import pandas_datareader as web
import pandas as pd


class Pyalgofetcher:
    """ This class does all the work."""
    def __init__(self, cfg):
        """ Construct the fetcher object """
        # Read the config file.
        self.process_config_data(cfg)

        self.feed_name = cfg.feed  # Feed(s) to run
        logging.debug("feed_name = %s", self.feed_name)

        self.history_dir = cfg.history_dir  # Output of this project
        logging.debug("history_dir = %s", self.history_dir)

        # Create the history_dir (if it doesn't exist). Allow it to be a symlink
        if not os.path.isdir(self.history_dir) and not os.path.islink(self.history_dir):
            os.mkdir(self.history_dir)

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
                logging.critical("init(): Unsupported output format parameter: %s",
                                 cfg.output_format)
                sys.exit(1)
        else:
            self.output_format = self.config_data['output_config']['file']['format']
        logging.info("Output format is: %s", self.output_format)
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
                logging.critical("init(): Unsupported compression: %s", cfg.compression)
                sys.exit(1)
        else:
            self.compression = self.config_data['output_config']['file']['format_args']['compression']
        logging.info("Compression is: %s", self.compression)

    def process_config_data(self, cfg):
        """ Read the config file, and the override file if it exists,
        and store the merged result in self.config_data.
        Also, write the result to the merge file if one is given.
        """
        self.config_file = cfg.config_file
        self.override_file = cfg.override_file
        self.merged_file = cfg.merged_file
        logging.debug("config_file = %s", self.config_file)
        logging.debug("override_file = %s", str(self.override_file))
        logging.debug("merged_file = %s", str(self.merged_file))
        # Read config data
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
        self.config_data = orig_config_data
        # print("Applying override_file_data: " + str(override_file_data))
        if override_file_data is not None:
            self.config_data = merge(orig_config_data, override_file_data)

        # Store the resulting merged data to a file (if given a 'merged_file'
        if self.merged_file is not None:
            # Ensure parent directory for merged file exists
            directory = Path(self.merged_file).parent
            if not os.path.exists(directory):
                os.makedirs(directory)
            # Write merged file
            with open(self.merged_file, 'w', encoding="utf8") as out_file:
                yaml.dump(self.config_data, out_file)

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
                     str(rowcount), abs_filename)
        if self.output_format == "csv":
            csv_header = self.config_data['output_config']['file']['format_args']['header']
            if str(csv_header).lower() == 'false':
                data_frame.to_csv(abs_filename, header=None, index=False)
            else:
                data_frame.to_csv(abs_filename, index=False)
        elif self.output_format == "json":
            orient = self.config_data['output_config']['file']['format_args']['orient']
            if str(orient).lower() == 'table':
                data_frame.to_json(abs_filename, orient="table")
            if str(orient).lower() == 'records':
                data_frame.to_json(abs_filename, orient="records", lines=True)
            else:
                logging.critical("Unsupported value of orient: %s", orient)
                sys.exit(1)
        else:
            logging.critical("write_df(): Unsupported output format parameter: %s",
                             self.output_format)
            sys.exit(1)

    def make_rel_filename(self, feed_api, feed):
        """ Create a filename given the feed parameters """
        rel_filename = feed_api
        rel_filename += "_" + feed
        rel_filename += "_" + self.end_date
        rel_filename += "_" + self.start_date
        rel_filename += "." + self.output_format
        # If compression is enabled, append the extension to the filename
        if self.compression is not None and self.compression.lower() != "none":
            rel_filename += "." + self.compression.replace(".", "")
        return rel_filename

    def process_pdr_feed(self, feed, feed_dir, feed_api):
        """ Process data that is read via the pandas datareader API """
        logging.info("Loading feed with api: " + feed_api + " feed:" + feed)
        args = self.config_data['feeds'][feed]['api_args']
        logging.debug("API args: %s", str(args))
        symbol = args['symbol']
        source = args['source']
        start = datetime.datetime.fromisoformat(self.start_date)
        end = datetime.datetime.fromisoformat(self.end_date)
        # Fetch the data into a dataframe
        # If there is no data for the date range given, this throws a "KeyError" on 'Date'
        try:
            data_frame = web.DataReader(symbol, source, start, end)
        except KeyError as key_exception:
            logging.error("No data found. Got KeyError: %s", str(key_exception))
            logging.critical("No data found for feed: %s for range: %s to %s",
                             feed, self.start_date, self.end_date)
            sys.exit(1)
        # Write the file
        rel_filename = self.make_rel_filename(feed_api, feed)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, data_frame)

    def process_fed_feed(self, feed, feed_dir, feed_api):
        """ Process data that is read from the New York Fed website (rest) API """
        logging.info("Loading feed with api: " + feed_api + " feed:" + feed)
        args = self.config_data['feeds'][feed]['api_args']
        logging.debug("API args: %s", str(args))
        #symbol = args['symbol'] # This was already used to calculate the feed_dir
        product_code = args['productCode']
        query = args['query']
        holding_types = args['holdingTypes']
        # Construct the query URL
        url = 'https://markets.newyorkfed.org/read?productCode=' + product_code
        url += '&startDt=' + self.start_date + '&endDt=' + self.end_date
        url += '&query=' + query + '&holdingTypes=' + holding_types + '&format=csv'
        # Fetch the data into a dataframe
        try:
            data_frame = pd.read_csv(url)
        except Exception as general_exception:
            logging.error("Failed to get data. Error: %s", str(general_exception))
            logging.critical("No data found for feed: %s for range: %s to %s",
                             feed, self.start_date, self.end_date)
            sys.exit(1)
        # Write the file
        rel_filename = self.make_rel_filename(feed_api, feed)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, data_frame)

    def process_sc_feed(self, feed, feed_dir, feed_api):
        """ Process data that is read from StockCharts """
        logging.info("Loading feed with api: " + feed_api + " feed:" + feed)
        logging.critical("SC NOT IMPLEMENTED YET")
        sys.exit(1)
        args = self.config_data['feeds'][feed]['api_args']
        logging.debug("API args: %s", str(args))
        #username = args['username']
        password = args['password']
        # Construct the query URL
        #TODO: stockcharts
        url = ''
        #url = 'https://markets.newyorkfed.org/read?productCode=' + product_code
        #url += '&startDt=' + self.start_date + '&endDt=' + self.end_date
        #url += '&query=' + query + '&holdingTypes=' + holding_types + '&format=csv'
        # Fetch the data into a dataframe
        try:
            data_frame = pd.read_csv(url)
        except Exception as general_exception:
            logging.error("Failed to get data. Error: %s", str(general_exception))
            logging.critical("No data found for feed: %s for range: %s to %s",
                             feed, self.start_date, self.end_date)
            sys.exit(1)
        # Write the file
        rel_filename = self.make_rel_filename(feed_api, feed)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, data_frame)

    def process_whysper_feed(self, feed, feed_dir, feed_api):
        """ Process data that is read from Whysper.io """
        logging.info("Loading feed with api: " + feed_api + " feed:" + feed)
        args = self.config_data['feeds'][feed]['api_args']
        logging.debug("API args: %s", str(args))
        #username = args['username']
        #password = args['password']
        # Construct the query URL
        # TODO: whysper feed
        url = ''
        # url = 'https://markets.newyorkfed.org/read?productCode=' + product_code
        # url += '&startDt=' + self.start_date + '&endDt=' + self.end_date
        # url += '&query=' + query + '&holdingTypes=' + holding_types + '&format=csv'
        # Fetch the data into a dataframe
        try:
            data_frame = pd.read_csv(url)
        except Exception as general_exception:
            logging.error("Failed to get data. Error: %s", str(general_exception))
            logging.critical("No data found for feed: %s for range: %s to %s",
                             feed, self.start_date, self.end_date)
            sys.exit(1)
        # Write the file
        rel_filename = self.make_rel_filename(feed_api, feed)
        abs_filename = os.path.normpath(os.path.join(feed_dir, rel_filename))
        self.write_df(abs_filename, data_frame)

    def create_feed_api_dir(self, feed, feed_api):
        """ Ensure the directory to hold the data for this feed exists. Return its path """
        feed_api_dir = os.path.normpath(os.path.join(self.history_dir, feed_api))
        if os.path.isdir(feed_api_dir):
            logging.debug("API Directory for feed:" + feed + " exists at:" + feed_api_dir)
        else:
            logging.debug("Creating API directory for feed:" + feed + " at:" + feed_api_dir)
            os.mkdir(feed_api_dir)
        hist_dir = os.path.normpath(os.path.join(feed_api_dir, feed))
        if os.path.isdir(hist_dir):
            logging.debug("Feed history directory for feed:" + feed + " exists at:" + hist_dir)
        else:
            logging.debug("Creating feed history directory for feed:" + feed + " at:" + hist_dir)
            os.mkdir(hist_dir)
        return hist_dir

    def process_feed(self, feed):
        """ Process the given feed
        """
        feed_cfg = self.config_data["feeds"][feed]
        logging.debug("Feed cfg: %s", str(feed_cfg))
        feed_api = feed_cfg['api']
        if feed_api == 'pdr':
            feed_dir = self.create_feed_api_dir(feed, feed_api)
            self.process_pdr_feed(feed, feed_dir, feed_api)
        elif feed_api == 'fed':
            feed_dir = self.create_feed_api_dir(feed, feed_api)
            self.process_fed_feed(feed, feed_dir, feed_api)
        elif feed_api == 'sc':
            feed_dir = self.create_feed_api_dir(feed, feed_api)
            self.process_sc_feed(feed, feed_dir, feed_api)
        else:
            logging.critical("Feed:" + feed + " has an invalid api:" + feed_api)
            sys.exit(1)

    def run(self):
        """ Run the feed loaders. If the given feed is "ALL" then load all of them.
        """
        if self.feed_name == "ALL":
            logging.info("Process all feeds")
        else:
            logging.info("Processing just feed: %s", self.feed_name)
        # Process the given feed, or ALL feeds.
        feeds = self.config_data['feeds']
        for feed in feeds:
            logging.debug("Feed: %s", str(feed))
            if self.feed_name in (feed, 'ALL'):
                logging.debug("Processing feed with name: %s", feed)
                self.process_feed(feed)
            else:
                logging.debug("Skipping feed with name: %s", feed)
        logging.info("Successfully finished processing")


def merge(dict_a, dict_b, path=None, update=True):
    """ Merge 'b' into 'a'
        https://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
    """
    # print("\nMerging: a=" + str(a) + " b=" + str(b) + " path=" + str(path) )
    if path is None:
        path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge(dict_a[key], dict_b[key], path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass  # same leaf value
            elif isinstance(dict_a[key], list) and isinstance(dict_b[key], list):
                for idx, val in enumerate(dict_b[key]):
                    dict_a[key][idx] = merge(dict_a[key][idx],
                                             dict_b[key][idx],
                                             path + [str(key), str(idx)],
                                             update=update)
            elif update:
                dict_a[key] = dict_b[key]
            else:
                raise Exception('Conflict at %s', (path + [str(key)]) )
        else:
            dict_a[key] = dict_b[key]
    return dict_a


def read_cli_args(argv):
    """ Read the CLI args and return sane settings
    """
    # Hard-coded Defaults
    log_level = "DEBUG"
    # Config file
    cur_dir = os.getcwd()
    config_file = os.path.normpath(os.path.join(cur_dir, "config.yaml"))
    override_file = os.path.normpath(os.path.join(cur_dir, "overrides.yaml"))
    merged_file = os.path.normpath(os.path.join(cur_dir, ".config.yaml"))
    # App specific
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
    parser.add_argument('-O', '--output-destinations',
                        action='store', type=str, dest="output_destinations",
                        help='Output Destinations. Currently, only supports "file"'
                        + '. Default: from config file',
                        default=output_format)
    parser.add_argument('-F', '--output-format',
                        action='store', type=str, dest="output_format",
                        help='Output format for files. csv and json are supported.'
                        + 'Default: from config file',
                        default=output_format)
    parser.add_argument('-C', '--compression',
                        action='store', type=str, dest="compression",
                        help='Compression type for files: None,gz, bz2, xz, or zip.'
                        + ' Default: from config file',
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
    """ Main program """
    # First create a merged config file
    app_cfg = read_cli_args(argv)
    #
    configure_logging(app_cfg)
    app = Pyalgofetcher(app_cfg)
    app.run()


if __name__ == "__main__":
    main(sys.argv[1:])
