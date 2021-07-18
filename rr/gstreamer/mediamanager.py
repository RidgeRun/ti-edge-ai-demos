#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from rr.gstreamer.gstmedia import GstMedia
from rr.gstreamer.gstmedia import GstMediaError


class MediaManagerError(RuntimeError):
    pass


class MediaManager():
    """
    Class that handles the medias

    Attributes
    ----------
    _pipeline : GstElement
        A private GStreamer pipeline object

    Methods
    -------
    create_media(desc : str)
        Creates the media object from a string description

    add_media(key : str, media : GstMedia obj):
        Install a new media into a dictionary
    """

    def __init__(self):
        """
        Constructor for the Media Gstreamer Manager object
        """

        gst.init(None)

        self._Dict = {}

    def create_media(self, desc):
        """Create a media object

        Parameters
        ----------
        desc : str
            The media description

        Raises
        ------
        MediaManagerError
            If the description fails to create the media

        Return
        ------
        media : GstMedia obj
        """

        try:
            gst_media = GstMedia()
            gst_media.create_media(desc)
            media = gst_media.get_media()
        except KeyError as e:
            raise MediaManagerError("Unable to create the media") from e
        return media

    def add_media(self, key, media):
        """Install a new media into a dictionary

        Parameters
        ----------
        media : obj
            The media object to add to dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to insert the media
        """

        try:
            self._Dict.update({key: media})
        except GLib.GError as e:
            raise MediaManagerError(
                "Unable to add the media to dictionary") from e

    def _get_media_dict(self):
        return self._Dict
