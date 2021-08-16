#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from argparse import ArgumentParser
import logging
import traceback

from rr.actions.action_manager import ActionManager
from rr.actions.action_manager import Action, ActionError
from rr.actions.action_manager import Filter, FilterError
from rr.actions.action_manager import Trigger, TriggerError
from rr.ai.ai_manager import AIManagerOnNewImage
from rr.config.app_config_loader import AppConfigLoader
from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import StreamManager
from rr.display.display_manager import DisplayManager


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


def parse_filters(config):
    filters = []
    for desc in config['filters']:
        filters.append(Filter.make(desc))

    return filters


def parse_actions(config):
    actions = []
    for desc in config['actions']:
        actions.append(Action.make(desc))

    return actions


def parse_triggers(config, actions, filters):
    triggers = []
    for desc in config['triggers']:
        triggers.append(Trigger.make(desc, actions, filters))

    return triggers


def create_action_manager(config):
    filters = parse_filters(config)
    actions = parse_actions(config)
    triggers = parse_triggers(config, actions, filters)

    return ActionManager(triggers)


def create_streams(config):
    streams = []
    for stream in config['streams']:
        desc = 'uridecodebin uri=%s ! videoconvert ! appsink sync=false qos=false async=false name=appsink' % (
            stream['uri'])
        media = GstMedia()
        media.create_media(stream['id'], desc)
        streams.append(media)

    return streams


def create_media_manager(streams):
    media_manager = MediaManager()

    for stream in streams:
        media_manager.add_media(stream.get_name(), stream)

    return media_manager


def create_display_manager(streams):
    display_manager = DisplayManager()

    for stream in streams:
        display_manager.add_stream(stream)

    return display_manager


def main():
    args = parse_args()

    error.verbose = args.verbose

    disp_width = '320'
    disp_height = '240'
    model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"

    config = AppConfigLoader()

    ai_manager = AIManagerOnNewImage(model, disp_width, disp_height)


#    stream_manager = StreamManager(
#        ai_manager,
#        media_manager,
#        model,
#        disp_width,
#        disp_height)

    try:
        config_dict = config.load(args.config_file)

        streams = create_streams(config_dict)

        media_manager = create_media_manager(streams)
        display_manager = create_display_manager(streams)
        action_manager = create_action_manager(config_dict)

    except Exception as e:
        error(e)


if __name__ == '__main__':
    main()
