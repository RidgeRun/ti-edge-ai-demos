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
import unittest

from rr.gstreamer.media_manager import MediaManager
from rr.gstreamer.media_manager import MediaManagerError


class TestMediaManager(unittest.TestCase):
    def setUp(self):
        desc = "videotestsrc is-live=true ! fakesink async=false"
        self.key = "setup"

        self.media_manager = MediaManager()

        self.media = self.media_manager.create_media(desc)

        self.media_manager.add_media(self.key, self.media)

    def testadd_media(self):
        dict = self.media_manager._get_media_dict()

        self.assertTrue(self.key in dict)

        self.assertEqual(self.media, dict[self.key])

    def testremove_media(self):
        dict = self.media_manager._get_media_dict()

        self.media_manager.remove_media(self.key)
        self.assertFalse(self.key in dict)

    def testplay_media(self):
        desc2 = "videotestsrc is-live=true pattern=colors ! fakesink async=false"
        key2 = "pattern_colors"

        media2 = self.media_manager.create_media(desc2)
        self.media_manager.add_media(key2, media2)

        self.media_manager.play_media()

    def teststop_media(self):
        self.media_manager.stop_media()


class TestMediaManagerFail(unittest.TestCase):
    def setUp(self):
        self.media_manager = MediaManager()

    def testadd_media(self):
        with self.assertRaisesRegex(MediaManagerError, "Invalid key or media"):
            self.media_manager.add_media(None, None)

        # Check dictionary it's empty
        dict = self.media_manager._get_media_dict()
        self.assertEqual(0, len(dict))

    def testremove_media(self):
        with self.assertRaisesRegex(MediaManagerError, "Invalid key"):
            self.media_manager.remove_media(None)

        with self.assertRaisesRegex(MediaManagerError, "Unable to find the key in the dictionary"):
            self.media_manager.remove_media(random.random())

    def testplay_media(self):
        desc = "videotestsrc is-live=true ! fakesink async=false state-error=3"
        key = "play_media"

        media = self.media_manager.create_media(desc)
        self.media_manager.add_media(key, media)

        with self.assertRaisesRegex(MediaManagerError, "Unable to start media"):
            self.media_manager.play_media()

        with self.assertRaisesRegex(MediaManagerError, "Invalid key or media"):
            self.media_manager.add_media(key, None)

    def teststop_media(self):
        desc = "videotestsrc is-live=true ! fakesink async=false state-error=5"
        key = "play_media"

        media = self.media_manager.create_media(desc)
        self.media_manager.add_media(key, media)
        self.media_manager.play_media()
        with self.assertRaisesRegex(MediaManagerError, "Unable to stop media"):
            self.media_manager.stop_media()


if __name__ == '__main__':
    unittest.main()
