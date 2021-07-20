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
    _Dict : dictionary
        A private dictionary to handle the medias

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
        media : GstMedia obj from a description
        """

        try:
            self.gst_media = GstMedia()
            self.gst_media.create_media(desc)

        except KeyError as e:
            raise MediaManagerError("Unable to create the media") from e

        return self.gst_media

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

        if key is None or media is None:
            raise MediaManagerError("Invalid key or media")

        self._Dict.update({key: media})

    def remove_media(self, key):
        """Remove media from dictionary

        Parameters
        ----------
        media : obj
            The media object to remove from dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to remove the media
        """

        if key is None:
            raise MediaManagerError("Invalid key")

        if key not in self._Dict:
            raise MediaManagerError("Unable to find the key in the dictionary")

        if self._Dict[key] is not None:
            del self._Dict[key]
            self._Dict[key] = None

        self._Dict.pop(key)

    def start_media(self):
        """Start the medias from dictionary

        Parameters
        ----------

        Raises
        ------
        """

        for key in self._Dict:
            try:
                self._Dict[key].play_media()
            except GstMediaError as e:
                raise MediaManagerError("Unable to start media") from e

    def _get_media_dict(self):
        return self._Dict
