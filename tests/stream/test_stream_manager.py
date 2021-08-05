#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import unittest
from unittest.mock import MagicMock

from rr.stream.stream_manager import StreamManager


class MockAiManager:
    def __init__(self):
        self.process = MagicMock()


class MockImage:
    pass


model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"
disp_width = 2040
disp_height = 1920
mock_image = MockImage()


class MockMediaManager:
    def install_callback(self, cb):
        self.cb = cb

    def play(self):
        self.cb(mock_image, model, disp_width, disp_height)


class TestStreamManager(unittest.TestCase):
    def test_success(self):
        media_manager = MockMediaManager()
        ai_manager = MockAiManager()

        stream_manager = StreamManager(ai_manager, media_manager)

        stream_manager.start()

        ai_manager.process.assert_called_with(
            mock_image, model, disp_width, disp_height)


if __name__ == '__main__':
    unittest.main()
