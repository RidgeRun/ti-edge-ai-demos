#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.gst_media import GstMediaError

w = 320
h = 240

MAX_STREAMS = 8
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# Define streams order in display
xpos = [0, w, 0, w, 2 * w, 2 * w, 3 * w, 3 * w]
ypos = [0, 0, h, h, 0, h, 0, h]


class DisplayManagerError(RuntimeError):
    pass


class DisplayManager():
    """
    Class that handles the display

    Attributes
    ----------
    _list : list
        A private list to manage streams

    Methods
    -------

    add_stream(key : str):
        Install a new stream in the display list

    remove_stream(key : str):
        Remove a stream from the display list

    create_display():
        Create the display media

    play_display():
        Play the display media

    stop_display():
        Stop the display media

    delete_display():
        Delete the display media

    """

    def __init__(self):
        """
        Constructor for the Display Manager object
        """

        self._media = GstMedia()
        self._display_desc = None
        self._list = []

    def add_stream(self, key):
        """
        Install a new stream in the display list
        """
        if key is None:
            raise DisplayManagerError("Invalid key")

        if not isinstance(key, str):
            raise DisplayManagerError("Invalid key")

        if self._display_desc is not None:
            raise DisplayManagerError(
                "Display already created, delete before adding a new stream")

        if MAX_STREAMS == len(self._list):
            raise DisplayManagerError("Max number of streams reached")

        if key not in self._list:
            self._list.append(key)
        else:
            raise DisplayManagerError(
                "Stream already exists in display manager")

    def remove_stream(self, key):
        """
        Remove a stream from the display list
        """
        if key is None:
            raise DisplayManagerError("Invalid key")

        if not isinstance(key, str):
            raise DisplayManagerError("Invalid key")

        if self._display_desc is not None:
            raise DisplayManagerError(
                "Display already created, delete before removing a stream")

        if key in self._list:
            self._list.remove(key)
        else:
            raise DisplayManagerError(
                "Stream doesn't exist in display manager")

    def create_display(self):
        """
        Create the display media
        """
        if self._display_desc is not None:
            raise DisplayManagerError("Display already created")

        if 0 == len(self._list):
            raise DisplayManagerError("No streams added")

        desc = "videomixer name=mixer "
        xpos_desc = ""
        ypos_desc = ""

        for i in range(len(self._list)):
            xpos_desc += " sink_" + str(i) + "::xpos=" + str(xpos[i])
            ypos_desc += " sink_" + str(i) + "::ypos=" + str(ypos[i])

        desc += xpos_desc
        desc += ypos_desc
        desc += " ! queue ! video/x-raw,width=" + str(DISPLAY_WIDTH) + ",height=" + str(
            DISPLAY_HEIGHT) + " ! kmssink force-modesetting=true sync=false async=false qos=false "

        for key in self._list:
            desc += " interpipesrc listen-to=" + key + " format=time ! queue ! videoscale ! video/x-raw,width=" + \
                str(w) + ",height=" + str(h) + " ! mixer. "

        self._display_desc = desc
        self._media.create_media("display", self._display_desc)

    def play_display(self):
        """
        Play the display media
        """
        if self._display_desc is None:
            raise DisplayManagerError("Display description not created yet")

        try:
            self._media.play_media()
        except GstMediaError as e:
            raise DisplayManagerError("Unable to start display") from e

    def stop_display(self):
        """
        Stop Display Manager
        """
        if self._display_desc is None:
            raise DisplayManagerError("Display description not created yet")

        try:
            self._media.stop_media()
        except GstMediaError as e:
            raise DisplayManagerError("Unable to stop display") from e

    def delete_display(self):
        """
        Deleter Display Manager description
        """
        if self._display_desc is None:
            raise DisplayManagerError("Display description not created yet")

        self.stop_display()

        try:
            self._media.delete_media()
        except GstMediaError as e:
            raise DisplayManagerError("Unable to delete display") from e

        self._display_desc = None

    def _get_stream_list(self):
        return self._list

    def _get_media(self):
        return self._media

    def _get_display_desc(self):
        return self._display_desc
