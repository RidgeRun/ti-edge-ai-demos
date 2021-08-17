#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from argparse import ArgumentParser
import logging
import traceback

import gi  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import GLib  # nopep8

from rr.config.app_config_loader import AppConfigLoader
from rr.smart_cctv import SmartCCTV


def error(e):
    if error.verbose:
        logging.error(traceback.format_exc())
    logging.error(e)

    if not error.verbose:
        logging.error("Execute with '-v' to get the full trace")


def parse_args():

    parser = ArgumentParser(description='AI CCTV system for smart cities')
    parser.add_argument('-f', dest='config_file', default='config.yaml',
                        help='configuration file used by the system.')
    parser.add_argument(
        '-v',
        dest='verbose',
        default=False,
        action='store_true',
        help='Print full stack trace of errors. Useful for debugging.')
    return parser.parse_args()


def main():
    args = parse_args()

    error.verbose = args.verbose

    config = AppConfigLoader()

    try:
        config_dict = config.load(args.config_file)
        server = SmartCCTV(config_dict)
    except Exception as e:
        error(e)

    try:
        server.start()
        print("Starting Smart CCTV server, press ctrl+c to interrupt...")
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print("Cleaning up.")
        server.stop()


if __name__ == '__main__':
    main()
