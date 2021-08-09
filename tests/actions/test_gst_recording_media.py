#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import unittest

import os
from rr.actions.gst_recording_media import GstRecordingMedia

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GstVideo', '1.0')  # nopep8
from gi.repository import Gst
from gi.repository import GstVideo
import numpy as np
import cv2 as cv

width = 320
height = 240
fmt = GstVideo.VideoFormat.RGBA
size = 320 * 240 * 4
data = np.zeros((size))


class MockImage():
    def __init__(self):
        self._pts = 0

    def get_width(self):
        return width

    def get_height(self):
        return height

    def get_format(self):
        return fmt

    def get_buffer(self):
        buf = Gst.Buffer.new_wrapped_full(0, data, size, 0, None, None)
        buf.pts = self._pts
        self._pts = self._pts + 33333333
        return buf


class TestGstRecordingMedia(unittest.TestCase):
    def test_recording_success(self):
        img = MockImage()
        rec = GstRecordingMedia()
        num_bufs = 10

        for i in range(num_bufs):
            rec.push_image(img)

        rec.stop_media()
        ret = None

        reader = cv.VideoCapture('/tmp/file.ts')
        self.assertEqual(True, reader.isOpened())

        for i in range(num_bufs):
            ret, frame = reader.read()
            self.assertEqual(True, ret)

        ret, frame = reader.read()
        self.assertEqual(False, ret)
        self.assertEqual(None, frame)


if __name__ == '__main__':
    unittest.main()
