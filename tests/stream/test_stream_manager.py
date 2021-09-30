#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import numpy as np
import time
import unittest
from unittest.mock import MagicMock

from bin.utils.getconfig import GetConfigYaml
from rr.actions.action_manager import ActionManager
from rr.actions.action_manager import Action
from rr.actions.action_manager import Filter
from rr.actions.action_manager import Trigger
from rr.ai.ai_manager import AIManagerOnNewImage
from rr.config.app_config_loader import AppConfigLoader
from rr.display.display_manager import DisplayManager
from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import OnNewImage
from rr.stream.stream_manager import StreamManager


class MockTriggerMedia:
    pass


default_config_file = "tests/test_config.yaml"
disp_width = 2040
disp_height = 1920
default_dimentions = 3
img_path = "./data/0004.jpg"


class SetUpConfigs:
    @classmethod
    def get_configs(cls, config):
        def configs(): return None
        configs.model_dir = config['model_params']['model']['detection']
        configs.model_params = config['model_params']
        configs.ai_model = GetConfigYaml(configs.model_dir)

        return configs


class SetUpStreams:
    @classmethod
    def get_streams(cls, config, configs):
        streams = []
        actions = []
        filters = []
        triggers = []

        for desc in config['filters']:
            filters.append(Filter.make(desc))

        for desc in config['actions']:
            actions.append(Action.make(desc))

        for desc in config['triggers']:
            triggers.append(Trigger.make(desc, actions, filters))

        for s in config['streams']:
            streams.append(GstMedia.make(s, triggers, configs))

        return streams


class SetUpStreamManager:
    def __init__(self, streams, model, disp_w, disp_h):
        self.ai_manager_dict = {}
        self.media_manager = MediaManager()
        self.display_manager = DisplayManager()
        self.action_manager = ActionManager()

        for s in streams:
            self.media_manager.add_media(s.get_name(), s)
            self.display_manager.add_stream(s)
            self.ai_manager_dict.update(
                {s.get_name(): AIManagerOnNewImage(model, disp_w, disp_h)})


class TestStreamManager(unittest.TestCase):
    def testsuccess(self):
        config_obj = AppConfigLoader()
        config = config_obj.load(default_config_file)

        configs = SetUpConfigs.get_configs(config)
        streams = SetUpStreams.get_streams(config, configs)

        model = configs.model_dir
        context = SetUpStreamManager(streams, model, disp_width, disp_height)

        context.action_manager.execute = MagicMock()
        context.display_manager.push_image = MagicMock()
        stream_manager = StreamManager(
            context.action_manager,
            context.ai_manager_dict,
            context.display_manager,
            context.media_manager,
            model,
            disp_width,
            disp_height)

        stream_manager.play()
        time.sleep(2)

        context.action_manager.execute.assert_called()
        context.display_manager.push_image.assert_called()


if __name__ == '__main__':
    unittest.main()
