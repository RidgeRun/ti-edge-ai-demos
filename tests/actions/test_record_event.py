#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import unittest

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GstVideo', '1.0')  # nopep8
from gi.repository import Gst
from gi.repository import GstVideo
import numpy as np
import cv2 as cv

from rr.actions.record_event import RecordEvent


width = 320
height = 240
fmt = "RGBA"
size = 320 * 240 * 4
data = np.zeros((size))


class mockMedia():
    def __init__(self, name):
        self.media_name = name

    def get_name(self):
        return self.media_name


class MockSample():
    def __init__(self):
        self._pts = 0

    def get_buffer(self):
        data = np.zeros((size))
        buf = Gst.Buffer.new_wrapped(data)
        buf.pts = self._pts
        buf.dts = self._pts
        buf.duration = 33333333
        self._pts = self._pts + 33333333
        return buf


class MockImage():
    def __init__(self, timestamp):
        self._sample = MockSample()
        self._timestamp = timestamp

    def get_width(self):
        return width

    def get_height(self):
        return height

    def get_format(self):
        return fmt

    def get_sample(self):
        return self._sample

    def get_timestamp(self):
        return self._timestamp


class MockFilter():
    def __init__(self, status):
        self.trigger_status = status

    def is_triggered(self):
        return self.trigger_status


class TestRecordEvent(unittest.TestCase):

    def test_record_event_success(self):
        rec_dir = '/tmp'
        timestamp = '2021-07-27-12:00:20'
        img = MockImage(timestamp)
        fil = MockFilter(True)
        num_bufs = 10
        rec_time = 15.0
        event_rec = RecordEvent("name", rec_dir, rec_time)

        media0 = mockMedia("media0")
        for i in range(num_bufs):
            event_rec.execute(media0, img, None, [fil])

        media1 = mockMedia("media1")
        for i in range(num_bufs):
            if i == 2:
                fil.trigger_status = False
            event_rec.execute(media1, img, rec_time, [fil])

        event_rec.stop_recordings()

        path_media0 = "/tmp/detection_recording_media0_" + timestamp + ".ts"
        path_media1 = "/tmp/detection_recording_media1_" + timestamp + ".ts"

        reader_media0 = cv.VideoCapture(path_media0)
        reader_media1 = cv.VideoCapture(path_media1)

        self.assertEqual(True, reader_media0.isOpened())
        self.assertEqual(True, reader_media1.isOpened())

    def test_not_recording_success(self):
        rec_dir = '/tmp'
        timestamp = '2022-08-27-12:00:20'
        img = MockImage(timestamp)
        fil = MockFilter(False)
        num_bufs = 10
        rec_time = 5.0
        event_rec = RecordEvent("name", rec_dir, rec_time)

        media2 = mockMedia("media2")
        for i in range(num_bufs):
            event_rec.execute(media2, img, None, [fil])

        path_media2 = "/tmp/detection_recording_media2_" + timestamp + ".ts"

        reader_media2 = cv.VideoCapture(path_media2)

        self.assertEqual(False, reader_media2.isOpened())


if __name__ == '__main__':
    unittest.main()
