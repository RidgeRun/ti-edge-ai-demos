#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from argparse import ArgumentParser
from rr.config.app_config_loader import AppConfigLoader
from rr.gstreamer.gst_media import GstMedia
import logging
import traceback


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
    gstmedia = GstMedia()

    try:
        config_dict = config.load(args.config_file)

        for stream in config_dict['streams']:
            pipeline = 'uridecodebin uri=%s ! videoconvert ! appsink sync=false qos=false async=false name=appsink' % (
                stream['uri'])
            gstmedia.create_media(pipeline)

    except RuntimeError as e:
        error(e)


if __name__ == '__main__':
    main()
