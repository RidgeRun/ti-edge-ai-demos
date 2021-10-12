#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst
from gi.repository import GLib

import unittest
from unittest.mock import MagicMock

from bin.utils.getconfig import GetConfigYaml
from rr.config.app_config_loader import AppConfigLoader
from rr.actions.action_manager import Trigger
from rr.display.display_manager import DisplayManager
from rr.display.display_manager import DisplayManagerError
from rr.gstreamer.gst_media import GstMedia

default_config_file = 'config.yaml'
default_model_key = 'detection'


def _get_media_State(media):
    return media.get_state(gst.CLOCK_TIME_NONE)[1]


def _parsed_configuration():
    def configs(): return None
    config_obj = AppConfigLoader()
    config_dict = config_obj.load(default_config_file)

    configs.model_params = config_dict['model_params']
    model_dir = configs.model_params['model'][default_model_key]
    configs.ai_model = GetConfigYaml(model_dir)

    return configs


def _create_stream(id, trigger_list):
    # Create a stream instance
    stream_desc = {
        "id": id,
        "uri": "rtsp://localhost:5000/stream",
        "triggers": ["trigger_name"]
    }

    # Mock a configuration
    configs = _parsed_configuration()
    return GstMedia.make(stream_desc, trigger_list, configs)


class MockTriggerAction:
    def __init__(self):
        self.execute = MagicMock()

    def get_name(self):
        return "mock_action"


class MockTriggerFilter1:
    def __init__(self):
        self.apply = MagicMock()

    def get_name(self):
        return "mock_filter1"


class MockTriggerFilter2:
    def __init__(self):
        self.apply = MagicMock()

    def get_name(self):
        return "mock_filter2"


class TestDisplayManager(unittest.TestCase):
    def setUp(self):
        self.display_manager = DisplayManager()

        # Create a trigger
        desc = {
            "name": "trigger_name",
            "action": "mock_action",
            "filters": ["mock_filter1", "mock_filter2"]
        }

        action = MockTriggerAction()
        filters = [MockTriggerFilter1(), MockTriggerFilter2()]

        trigger = Trigger.make(desc, [action], filters)
        trigger.get_name = MagicMock(return_value=desc['name'])

        # Create a stream instance
        self.stream_desc = {
            "id": "stream0",
            "uri": "rtsp://localhost:5000/stream",
            "triggers": ["trigger_name"]
        }

        configs = _parsed_configuration()
        self.stream = GstMedia.make(self.stream_desc, [trigger], configs)

        self.display_manager.add_stream(self.stream)
        self.display_media = self.display_manager._get_media()

    def test_add_stream(self):
        list = self.display_manager._get_stream_list()
        self.assertTrue(self.stream.get_name() in list)

    def test_remove_stream(self):
        self.display_manager.remove_stream(self.stream_desc['id'])
        list = self.display_manager._get_stream_list()
        self.assertTrue(self.stream.get_name() not in list)

    def test_create_display(self):
        self.display_manager.create_display()

        media_obj = self.display_manager._get_media()
        self.assertEqual("display", media_obj.get_name())

    def test_play_display(self):
        self.test_create_display()
        media_state = _get_media_State(self.display_media.get_media())
        self.assertEqual(gst.State.NULL, media_state)
        self.display_manager.play_display()
        media_state = _get_media_State(self.display_media.get_media())
        self.assertEqual(gst.State.PLAYING, media_state)

    def test_stop_display(self):
        self.test_play_display()
        display_media = self.display_manager._get_media()
        self.display_manager.stop_display()
        media_state = _get_media_State(self.display_media.get_media())
        self.assertEqual(gst.State.NULL, media_state)

    def test_delete_display(self):
        self.test_create_display()
        self.display_manager.delete_display()
        self.assertEqual(None, self.display_manager._get_display_desc())

    def test_full_sequence(self):
        self.test_stop_display()
        self.display_manager.stop_display()
        self.display_manager.delete_display()
        self.assertEqual(None, self.display_manager._get_display_desc())


class TestDisplayManagerFail(unittest.TestCase):
    def setUp(self):
        self.display_manager = DisplayManager()

        # Create a trigger
        desc = {
            "name": "trigger_name",
            "action": "mock_action",
            "filters": ["mock_filter1", "mock_filter2"]
        }

        action = MockTriggerAction()
        filters = [MockTriggerFilter1(), MockTriggerFilter2()]

        self.trigger = Trigger.make(desc, [action], filters)
        self.trigger.get_name = MagicMock(return_value=desc['name'])

        # Create a stream instance
        self.stream_desc = {
            "id": "stream0",
            "uri": "rtsp://localhost:5000/stream",
            "triggers": ["trigger_name"]
        }

        configs = _parsed_configuration()
        self.stream = GstMedia.make(self.stream_desc, [self.trigger], configs)

        self.display_manager.add_stream(self.stream)

    def test_add_stream_none(self):
        with self.assertRaisesRegex(DisplayManagerError, "Invalid media object"):
            self.display_manager.add_stream(None)

    def test_add_stream_duplicated(self):
        with self.assertRaisesRegex(DisplayManagerError, "Stream already exists in display manager"):
            self.display_manager.add_stream(self.stream)

    def test_add_stream_after_created(self):
        self.display_manager.create_display()
        with self.assertRaisesRegex(DisplayManagerError, "Display already created, delete before adding a new stream"):
            self.display_manager.add_stream("stream1")

    def test_add_stream_exceed_limit(self):
        stream1 = _create_stream("stream1", [self.trigger])
        self.display_manager.add_stream(stream1)

        stream2 = _create_stream("stream2", [self.trigger])
        self.display_manager.add_stream(stream2)

        stream3 = _create_stream("stream3", [self.trigger])
        self.display_manager.add_stream(stream3)

        stream4 = _create_stream("stream4", [self.trigger])
        self.display_manager.add_stream(stream4)

        stream5 = _create_stream("stream5", [self.trigger])
        self.display_manager.add_stream(stream5)

        stream6 = _create_stream("stream6", [self.trigger])
        self.display_manager.add_stream(stream6)

        stream7 = _create_stream("stream7", [self.trigger])
        self.display_manager.add_stream(stream7)
        with self.assertRaisesRegex(DisplayManagerError, "Max number of streams reached"):
            stream8 = _create_stream("stream8", [self.trigger])
            self.display_manager.add_stream(stream8)

    def test_remove_stream_none(self):
        with self.assertRaisesRegex(DisplayManagerError, "Invalid key"):
            self.display_manager.remove_stream(None)

    def test_remove_stream_not_string(self):
        with self.assertRaisesRegex(DisplayManagerError, "Invalid key"):
            self.display_manager.remove_stream(1)

    def test_remove_stream_invalid(self):
        with self.assertRaisesRegex(DisplayManagerError, "Stream doesn't exist in display manager"):
            self.display_manager.remove_stream("a_invalid_key")

    def test_remove_stream_after_created(self):
        self.display_manager.create_display()
        with self.assertRaisesRegex(DisplayManagerError, "Display already created, delete before removing a stream"):
            self.display_manager.remove_stream(self.stream_desc['id'])

    def test_create_display_empty(self):
        self.display_manager.remove_stream(self.stream_desc['id'])
        with self.assertRaisesRegex(DisplayManagerError, "No streams added"):
            self.display_manager.create_display()

    def test_create_display_duplicated(self):
        self.display_manager.create_display()
        with self.assertRaisesRegex(DisplayManagerError, "Display already created"):
            self.display_manager.create_display()

    def test_play_display_not_created(self):
        self.display_manager.remove_stream(self.stream_desc['id'])
        with self.assertRaisesRegex(DisplayManagerError, "No streams added"):
            self.display_manager.play_display()

    def test_stop_display_not_created(self):
        self.display_manager.remove_stream(self.stream_desc['id'])
        with self.assertRaisesRegex(DisplayManagerError, "Display description not created yet"):
            self.display_manager.stop_display()

    def test_delete_display_not_created(self):
        self.display_manager.remove_stream(self.stream_desc['id'])
        with self.assertRaisesRegex(DisplayManagerError, "Display description not created yet"):
            self.display_manager.stop_display()


if __name__ == '__main__':
    unittest.main()
