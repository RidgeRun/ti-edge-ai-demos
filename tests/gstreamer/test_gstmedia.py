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

from rr.gstreamer.gstmedia import GstMedia
from rr.gstreamer.gstmedia import GstMediaError


def _get_mediaState(media):
    return media.get_state(gst.CLOCK_TIME_NONE)[1]


class TestGstMedia(unittest.TestCase):
    def setUp(self):
        self.desc = "videotestsrc is-live=true ! fakesink async=false"

        self.gstmedia = GstMedia()

        self.gstmedia.create_media(self.desc)

    def testcreate_media(self):
        self.assertTrue(isinstance(self.gstmedia.get_media(), gst.Pipeline))

    def testdelete_media(self):
        self.gstmedia.delete_media()
        assert self.gstmedia.get_media() is None, "Failed to delete the media object properly"

    def testplay_media(self):
        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertEqual(gst.State.NULL, media_state)

        self.gstmedia.play_media()
        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertEqual(gst.State.PLAYING, media_state)

    def teststop_media(self):
        self.gstmedia.play_media()
        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertEqual(gst.State.PLAYING, media_state)

        self.gstmedia.stop_media()

        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertEqual(gst.State.NULL, media_state)

    def testdelete_multiple_times(self):
        self.gstmedia.delete_media()
        assert self.gstmedia.get_media() is None, "Failed to delete the media object properly"
        self.gstmedia.delete_media()
        assert self.gstmedia.get_media() is None, "Failed to delete the media object properly"


class TestGstMediaFail(unittest.TestCase):
    def testcreate_media(self):
        # Force desc to make media fail
        self.desc = "videotestsrc is-live=true ! "
        self.gstmedia = GstMedia()

        with self.assertRaisesRegex(GstMediaError, "Unable to create the media"):
            self.gstmedia.create_media(self.desc)

    def testplay_media(self):
        # Force blocking of playing state
        self.desc = "fakesrc ! fakesink async=false state-error=3"
        self.gstmedia = GstMedia()
        self.gstmedia.create_media(self.desc)

        with self.assertRaisesRegex(GstMediaError, "Unable to play the media"):
            self.gstmedia.play_media()

        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertNotEqual(gst.State.PLAYING, media_state)

    def teststop_media(self):
        # Force blocking of stopped state
        self.desc = "fakesrc ! fakesink async=false state-error=5"
        self.gstmedia = GstMedia()
        self.gstmedia.create_media(self.desc)

        self.gstmedia.play_media()
        with self.assertRaisesRegex(GstMediaError, "Unable to stop the media"):
            self.gstmedia.stop_media()

        media_state = _get_mediaState(self.gstmedia.get_media())
        self.assertNotEqual(gst.State.PLAYING, media_state)


if __name__ == '__main__':
    unittest.main()
