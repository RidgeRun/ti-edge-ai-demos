#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import time
from rr.gstreamer.gst_media import GstMediaError as MediaError

STREAM_START_DELAY_INTERVAL = 0.5


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

    def __init__(self, stream):
        """
        Constructor for the Media Gstreamer Manager object
        """

        self._stream = stream
        self._appsink_dict = {}

        self.callback = None

    def add_media(self, key, appsink):
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

        if (key is None) or (appsink is None):
            raise MediaManagerError("Invalid key or media")

        self._appsink_dict.update({key: appsink})

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

        if key not in self._appsink_dict:
            raise MediaManagerError("Unable to find the key in the dictionary")

        self._appsink_dict.pop(key)

    def play_media(self):
        """Start the medias from dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to play the medias
        """

        for appsink in self._appsink_dict.values():
            try:
                appsink.play_media()
                time.sleep(STREAM_START_DELAY_INTERVAL)
            except MediaError as e:
                raise MediaManagerError("Unable to start media") from e

        try:
            self._stream.play_media()
            time.sleep(STREAM_START_DELAY_INTERVAL)
        except MediaError as e:
            raise MediaManagerError("Unable to start media") from e

    def stop_media(self):
        """Stop the medias from dictionary

        Raises
        ------
        MediaManagerError
            If the description fails to stop the medias
        """

        for appsink in self._appsink_dict.values():
            try:
                appsink.stop_media()
            except MediaError as e:
                raise MediaManagerError("Unable to stop media") from e
            try:
                appsink.delete_media()
            except MediaError as e:
                raise MediaManagerError("Unable to delete media") from e

        try:
            self._stream.stop_media()
            time.sleep(STREAM_START_DELAY_INTERVAL)
        except MediaError as e:
            raise MediaManagerError("Unable to start media") from e

    def install_image_callback(self, callback):
        for key, appsink in self._appsink_dict.items():
            try:
                appsink.install_image_callback(callback[key])
            except MediaError as e:
                raise MediaManagerError(
                    "Unable to install the image callback") from e

    def _get_media_dict(self):
        return self._appsink_dict
