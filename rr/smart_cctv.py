#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>


from rr.actions.action_manager import ActionManager
from rr.actions.action_manager import Action, ActionError
from rr.actions.action_manager import Filter, FilterError
from rr.actions.action_manager import Trigger, TriggerError
from rr.ai.ai_manager_mock import AIManagerOnNewImage
from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import StreamManager
from rr.display.display_manager import DisplayManager

disp_width = '320'
disp_height = '240'
model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"


class SmartCCTV:

    def _parse_filters(self, config):
        filters = []
        for desc in config['filters']:
            filters.append(Filter.make(desc))

        return filters

    def _parse_actions(self, config):
        actions = []
        for desc in config['actions']:
            actions.append(Action.make(desc))

        return actions

    def _parse_triggers(self, config, actions, filters):
        triggers = []
        for desc in config['triggers']:
            triggers.append(Trigger.make(desc, actions, filters))

        return triggers

    def _create_action_manager(self, config):
        filters = self._parse_filters(config)
        actions = self._parse_actions(config)
        triggers = self._parse_triggers(config, actions, filters)

        return ActionManager(triggers)

    def _create_streams(self, config):
        streams = []
        for stream in config['streams']:
            desc = 'uridecodebin uri=%s ! videoconvert ! video/x-raw,width=320,height=240,format=RGB ! appsink sync=false qos=false async=false name=appsink' % (
                stream['uri'])
            media = GstMedia()
            media.create_media(stream['id'], desc)
            streams.append(media)

        return streams

    def _create_media_manager(self, streams):
        media_manager = MediaManager()

        for stream in streams:
            media_manager.add_media(stream.get_name(), stream)

        return media_manager

    def _create_display_manager(self, streams):
        display_manager = DisplayManager()

        for stream in streams:
            display_manager.add_stream(stream)

        return display_manager

    def _create_ai_manager(self, model, disp_width, disp_height):
        return AIManagerOnNewImage(model, disp_width, disp_height)

    def __init__(self, config):
        streams = self._create_streams(config)
        media_manager = self._create_media_manager(streams)
        display_manager = self._create_display_manager(streams)
        action_manager = self._create_action_manager(config)
        ai_manager = self._create_ai_manager(model, disp_width, disp_height)

        self._stream_manager = StreamManager(
            action_manager,
            ai_manager,
            display_manager,
            media_manager,
            model,
            disp_width,
            disp_height)

    def start(self):
        self._stream_manager.play()

    def stop(self):
        self._stream_manager.stop()
