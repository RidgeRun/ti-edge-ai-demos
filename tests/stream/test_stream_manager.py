#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import unittest
from unittest.mock import MagicMock

from rr.ai.ai_manager import AIManagerOnNewImage
from rr.gstreamer.imedia import IMedia
from rr.gstreamer.media_manager import MediaManager
from rr.stream.stream_manager import StreamManager
from rr.stream.stream_manager import OnNewImage

model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"
disp_width = 2040
disp_height = 1920


class TestStreamManager(unittest.TestCase):
    def setUp(self):
        self.mock_on_new_prediction_cb = MagicMock()
        self.mock_on_new_postprocess_cb = MagicMock()

        ai_manager = AIManagerOnNewImage(model, disp_width, disp_height,
                                         self.mock_on_new_prediction_cb,
                                         self.mock_on_new_postprocess_cb)

        desc = "videotestsrc is-live=true ! fakesink async=false"
        key = "media1"
        media = IMedia()
        media.create_media(desc)

        mock_on_new_image_cb = MagicMock()

        media_manager = MediaManager()
        media_manager.add_media(key, media)
        media_manager.push_buffer(mock_on_new_image_cb)

        stream_manager = StreamManager(ai_manager, media_manager)

        mock_on_new_image_cb.assert_called_once()

    def teststream(self):
        pass


if __name__ == '__main__':
    unittest.main()
