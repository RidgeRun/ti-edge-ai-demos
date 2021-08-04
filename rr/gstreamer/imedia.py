#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from rr.gstreamer.gst_media import GstMedia as Media
from rr.gstreamer.gst_media import GstMediaError as MediaError


class IMediaError(RuntimeError):
    pass


class IMedia(Media):
    """
    Class that interfaces the media handler

    Methods
    -------
    create_media(desc : str)
        Creates the media object from a string description

    delete_media()
        Deletes the media object

    play_media()
        Set the media state to playing

    stop_media()
        Set the media state to stopped

    get_media()
        Getter for the media object
    """

    def __init__(self):
        """
        Constructor for the Media Gstreamer Manager object
        """

        self.media = Media()

    def create_media(self, desc):
        """Creates the media object from a string description

        Parameters
        ----------
        desc : str
            The media description to create

        Raises
        ------
        IMediaError
            If the description fails to create the media
        """

        try:
            self.media.create_media(desc)
        except MediaError as e:
            raise IMediaError("Unable to create the media") from e

    def delete_media(self):
        """Deletes the media object

        Raises
        ------
        IMediaError
            If could not delete the media
        """

        try:
            self.media.delete_media()
        except MediaError as e:
            raise IMediaError("Unable to delete the media") from e

    def play_media(self):
        """Set the media state to playing

        Raises
        ------
        IMediaError
            If couldn't set the media state to playing
        """

        try:
            self.media.play_media()
        except MediaError as e:
            raise IMediaError("Unable to play the media") from e

    def stop_media(self):
        """Set the media state to stopped

        Raises
        ------
        IMediaError
            If couldn't set the media state to stopped
        """
        try:
            self.media.stop_media()
        except MediaError as e:
            raise IMediaError("Unable to stop the media") from e

    def push_buffer(self, on_new_buffer):
        """

        Raises
        ------
        IMediaError
        """
        try:
            self.media.push_buffer(on_new_buffer)
        except MediaError as e:
            raise IMediaError("Unable to push buffer with the media") from e

    def get_media(self):
        """Getter for the media object

        Returns
        -------
        ret : media object
            The media object

        Raises
        ------
        IMediaError
            If couldn't set the media state to stopped
        """

        try:
            ret = self.media.get_media()
        except MediaError as e:
            raise IMediaError("Invalid media") from e

        return ret
