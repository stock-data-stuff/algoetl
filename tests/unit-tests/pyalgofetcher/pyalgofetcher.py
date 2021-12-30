#!/usr/bin/env python3

import os
import sys
import argparse
from lib.shellcmd import run_command
import logging


class Pyalgofetcher:
    def __init__(self, cfg):
        # Arguments
        self.config_file = cfg.config_file  # Config file
        self.history_dir = cfg.history_dir  # Output of this project
        self.feed_name = cfg.feed  # Feed to run
        logging.debug("config_file = " + self.config_file)
        logging.debug("history_dir = " + self.history_dir)
        logging.debug("feed_name = " + self.feed_name)
        # Calculate some parameters
        self.feed_dir = self.set_feed_dir()
        logging.debug("feed_dir = " + self.feed_dir)

    def set_feed_dir(self):
        """ Specify for the Feed Implementation to run
            Errors out if the feed directory is not found.
        """
        local_feed = os.path.normpath(os.path.join(os.getcwd(), "feed-scripts", self.feed_name))

        feed_dir = None
        if os.path.isdir(local_feed):
            feed_dir = local_feed
        else:
            logging.warning("local feed directory does not exist: " + local_feed)

        if feed_dir is None:
            logging.critical("Could not find directory for feed: " + self.feed_name)
            sys.exit(1)

        if not os.path.isdir(feed_dir):
            logging.critical("feed_dir is not a directory: " + feed_dir)
            sys.exit(1)

        return feed_dir

    def execute_feed(self):
        """ Execute the specified feed
        """
        # The Algorithm is:
        #   - Create and cd into working directory "<HISTORY_DIR>/<feed>"
        #   - Execute "<feed_dir>/<feed_script>"

        # Create the history_dir (if it doesn't exist)
        if not os.path.isdir(self.history_dir):
            os.mkdir(self.history_dir)

        # Create the Working Directory for the feed
        working_dir = os.path.normpath(os.path.join(self.history_dir,
                                                    self.feed_name))
        if not os.path.isdir(working_dir):
                os.mkdir(working_dir)
        # Traverse this way in case we change the way working_dir is set
        conf_file = os.path.normpath(os.path.join(working_dir,
                                                  "../..",
                                                  "config.yaml"))
        if not os.path.isfile(conf_file):
            logging.error("Config file is missing: " + conf_file)
            sys.exit(1)

        # Each directory should have a script with this name
        feed_script = "process_feed.py"

        command = os.path.normpath(os.path.join(self.feed_dir,
                                                feed_script))
        cmd = "cd " + working_dir + " && " + command
        logging.info("Executing command: " + cmd)
        rc = run_command(cmd)
        if rc != 0:
            logging.error("Command failed")
            sys.exit(rc)


def read_cli_args(argv):
    """ Read the CLI args and return sane settings
    """

    # Hard-coded Defaults
    cur_dir = os.getcwd()
    log_level = "DEBUG"
    config_file = os.path.normpath(os.path.join(cur_dir, "config.yaml"))
    history_dir = os.path.normpath(os.path.join(cur_dir, "feed-history"))
    feed = 'ALL'

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
    app.execute_feed()


if __name__ == "__main__":
    main(sys.argv[1:])
