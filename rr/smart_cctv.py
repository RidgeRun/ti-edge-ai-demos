#!/usr/bin/env python3
#  Copyright (C) 2021-2022 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#           Emmanuel Madrigal <emmanuel.madrigal@ridgerun.com>

from typing import List

from bin.utils.getconfig import GetConfigYaml
from rr.actions.action_manager import ActionManager
from rr.actions.action_manager import Action, ActionError
from rr.actions.action_manager import Filter, FilterError
from rr.actions.action_manager import Trigger, TriggerError
from rr.ai.ai_manager import AIManagerOnNewImage
from rr.gstreamer.gst_input import GstInput
from rr.gstreamer.gst_stream import GstStream
from rr.gstreamer.gst_preproc import GstPreProc
from rr.gstreamer.gst_appsink import GstAppSink
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import StreamManager
from rr.display.display_manager import DisplayManager


class SmartCCTV:
    def _parse_configs(self, config):
        def configs(): return None

        model_params = self._parse_model_params(config)
        configs.model_params = config['model_params']

        model_dir = model_params['model']['detection']
        configs.ai_model = GetConfigYaml(model_dir)

        return configs

    def _parse_model_params(self, config):
        model_params = config['model_params']
        return model_params

    def _parse_streams(self, config):
        streams_dict = config['streams']
        return streams_dict

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

    def _create_action_manager(self):
        return ActionManager()

    def _create_streams(self, config):
        filters = self._parse_filters(config)
        actions = self._parse_actions(config)
        triggers = self._parse_triggers(config, actions, filters)

        configs = self._parse_configs(config)

        stream = GstStream.make(config['streams'], configs)

        appsinks = []
        for desc in config['streams']:
            appsinks.append(GstAppSink.make(desc, triggers))

        input = GstInput(stream, appsinks)

        return input

    def _create_media_manager(self, stream, appsinks):
        media_manager = MediaManager(stream)

        for appsink in appsinks:
            media_manager.add_media(appsink.get_name(), appsink)

        return media_manager

    def _create_display_manager(self, streams):
        display_manager = DisplayManager()

        for stream in streams:
            display_manager.add_stream(stream)

        return display_manager

    def _create_ai_manager(self, config):
        model_params = self._parse_model_params(config)
        self.model = model_params['model']['detection']
        self.disp_width = model_params['disp_width']
        self.disp_height = model_params['disp_height']

        return AIManagerOnNewImage(
            self.model, self.disp_width, self.disp_height)

    def __init__(self, config):
        # Make sure the AI managers are the first classes to be created, otherwise
        # the engine will fail to start
        ai_manager_dict = {}
        for key in self._parse_streams(config):
            ai_manager_dict.update(
                {key['id']: self._create_ai_manager(config)})

        input = self._create_streams(config)
        media_manager = self._create_media_manager(input.stream, input.appsink)
        display_manager = self._create_display_manager(input.appsink)
        action_manager = self._create_action_manager()

        self._stream_manager = StreamManager(
            action_manager,
            ai_manager_dict,
            display_manager,
            media_manager,
            self.model,
            self.disp_width,
            self.disp_height)

    def start(self):
        self._stream_manager.play()

    def stop(self):
        self._stream_manager.stop()
