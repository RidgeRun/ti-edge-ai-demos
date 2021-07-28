#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from rr.gstreamer.imedia import IMediaError


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
    add_media(key : str, media : media obj):
        Install a new media into the dictionary

    remove_media(key : str):
        Remove media from dictionary

    play_media():
        Play the medias from dictionary

    stop_media():
        Stop the medias from dictionary

    """

    def __init__(self):
        """
        Constructor for the Media Gstreamer Manager object
        """

        self._Dict = {}

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

        if (key is None) or (media is None):
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
            self._Dict[key] = None

        self._Dict.pop(key)

    def play_media(self):
        """Start the medias from dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to play the medias
        """

        for key in self._Dict:
            try:
                self._Dict[key].play_media()
            except IMediaError as e:
                raise MediaManagerError("Unable to start media") from e

    def stop_media(self):
        """Stop the medias from dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to stop the medias
        """

        for key in self._Dict:
            try:
                self._Dict[key].stop_media()
            except IMediaError as e:
                raise MediaManagerError("Unable to stop media") from e

    def _get_media_dict(self):
        return self._Dict
