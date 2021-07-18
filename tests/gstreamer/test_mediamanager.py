#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from rr.gstreamer.mediamanager import MediaManager
from rr.gstreamer.mediamanager import MediaManagerError
import unittest


class TestMediaManager(unittest.TestCase):
    def setUp(self):
        desc = "videotestsrc ! fakesink"
        self.key = "setup"

        self.mediamanager = MediaManager()

        self.media = self.mediamanager.create_media(desc)

        self.mediamanager.add_media(self.key, self.media)

    def testadd_media(self):
        dict = self.mediamanager._get_media_dict()

        self.assertTrue(self.key in dict)

        self.assertEqual(self.media, dict[self.key])


if __name__ == '__main__':
    unittest.main()
