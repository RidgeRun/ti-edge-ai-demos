#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

import random
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

    def testremove_media(self):
        dict = self.mediamanager._get_media_dict()

        self.mediamanager.remove_media(self.key)
        self.assertFalse(self.key in dict)

    def teststart_media(self):
        desc2 = "videotestsrc pattern=colors ! fakesink"
        key2 = "pattern_colors"

        media2 = self.mediamanager.create_media(desc2)
        self.mediamanager.add_media(key2, media2)

        self.mediamanager.start_media()


class TestMediaManagerFail(unittest.TestCase):
    def setUp(self):
        self.mediamanager = MediaManager()

    def testadd_media(self):
        with self.assertRaisesRegex(MediaManagerError, "Invalid key or media"):
            self.mediamanager.add_media(None, None)

        # Check dictionary it's empty
        dict = self.mediamanager._get_media_dict()
        self.assertEqual(0, len(dict))

    def testremove_media(self):
        with self.assertRaisesRegex(MediaManagerError, "Invalid key"):
            self.mediamanager.remove_media(None)

        with self.assertRaisesRegex(MediaManagerError, "Unable to find the key in the dictionary"):
            self.mediamanager.remove_media(random.random())


if __name__ == '__main__':
    unittest.main()
