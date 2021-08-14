#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from argparse import ArgumentParser
import logging
import traceback

from rr.actions.action_manager import ActionManager
from rr.actions.action_manager import Trigger, TriggerError
from rr.ai.ai_manager import AIManagerOnNewImage
from rr.config.app_config_loader import AppConfigLoader
from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import StreamManager


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

    disp_width = '320'
    disp_height = '240'
    model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"

    config = AppConfigLoader()
    ai_manager = AIManagerOnNewImage(model, disp_width, disp_height)
    media_manager = MediaManager()

    stream_manager = StreamManager(
        ai_manager,
        media_manager,
        model,
        disp_width,
        disp_height)

    try:
        config_dict = config.load(args.config_file)

        for stream in config_dict['streams']:
            desc = 'uridecodebin uri=%s ! videoconvert ! appsink sync=false qos=false async=false name=appsink' % (
                stream['uri'])
            gstmedia = GstMedia()
            gstmedia.create_media(stream['id'], desc)
            media_manager.add_media(stream['id'], gstmedia)

    except RuntimeError as e:
        error(e)


if __name__ == '__main__':
    main()
