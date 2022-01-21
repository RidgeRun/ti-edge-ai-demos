#!/usr/bin/env python3

#  Copyright (C) 2021-2022 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#           Emmanuel Madrigal <emmanuel.madrigal@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from bin.utils.getconfig import GetConfigYaml

SECONDS_TO_NANOSECONDS = 1e9


class GstMediaError(RuntimeError):
    pass


class GstMedia():
    """
    Class that creates the GStreamer input stream handler
    Attributes
    ----------
    _pipeline : GstElement
        A private GStreamer pipeline object
    _triggers : List(Trigger)
        An optional list of triggers to execute on each image

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
        Getter for the private media object
    get_output_name()
        Returns the name of the one or many outputs
    """

    def __init__(self):
        """
        Constructor for the GStreamer Media object
        """

        gst.init(None)

        self._name = None
        self._pipeline = None
        self._output_name = []

    def create_media(self, name, desc):
        """Creates the media object from a string description
        Parameters
        ----------
        desc : str
            The media description to create
        Raises
        ------
        GstMediaError
            If the description fails to create the media
        """

        print("Creating media:")
        print("   Name: " + name)
        print("   Description: " + desc)

        try:
            self._pipeline = gst.parse_launch(desc)
            self._name = name
        except GLib.GError as e:
            raise GstMediaError("Unable to create the media") from e

    def delete_media(self):
        """Deletes the media object
        """

        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None

    def play_media(self):
        """Set the media state to playing
        Raises
        ------
        GstMediaError
            If couldn't set the media state to playing
        """

        print("Playing media: " + self._name)
        ret = self._pipeline.set_state(gst.State.PLAYING)
        if gst.StateChangeReturn.FAILURE == ret:
            raise GstMediaError("Unable to play the media")

    def stop_media(self):
        """Set the media state to stopped
        Raises
        ------
        GstMediaError
            If couldn't set the media state to stopped
        """

        print("Stopping media: " + self._name)
        # Nothing to be done if the pipe is not running
        ret, current, pending = self._pipeline.get_state(gst.CLOCK_TIME_NONE)
        if current != gst.State.PLAYING:
            return

        # Send an EOS and wait 3 seconds for the EOS to arrive before closing
        timeout = 3 * SECONDS_TO_NANOSECONDS
        print("Sending EOS: " + self._name)
        eos = self._pipeline.get_by_name("eos")
        eos.send_event(gst.Event.new_eos())
        self._pipeline.get_bus().timed_pop_filtered(timeout, gst.MessageType.EOS)

        print("Setting pipeline to NULL: " + self._name)
        ret = self._pipeline.set_state(gst.State.NULL)
        if gst.StateChangeReturn.FAILURE == ret:
            raise GstMediaError("Unable to stop the media")
        print("Media Stopped: " + self._name)

    def get_name(self):
        """Getter for the private media name
        """
        return self._name

    def get_media(self):
        """Getter for the private media object
        """
        return self._pipeline

    def get_output_name(self):
        """Returns the name of the one or many outputs

        Returns:
            List: List with names of outputs
        """

        return self._output_name


class GstUtils():
    def __init__(self):
        pass

    def buffer_new_wrapped(data):
        return gst.Buffer.new_wrapped(data)

    def buffer_new_wrapped_full(data, size):
        return gst.Buffer.new_wrapped_full(0, data, size, 0, None, None)

    def sample_new(buffer, caps):
        return gst.Sample.new(buffer, caps, None, None)


class GstImage():
    def __init__(
            self,
            width,
            height,
            format,
            sample,
            gst_media_obj):
        self.sample = sample
        self.gst_media_obj = gst_media_obj

        self._gst_memory_obj = None
        self.minfo = None

        self.width = width
        self.height = height
        self.format = format

        # Map the buffer
        self.map_flags = gst.MapFlags.READ
        self._map_buffer()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_format(self):
        return self.format

    def get_data(self):
        return self.minfo.data

    def get_sample(self):
        return self.sample

    def get_media(self):
        return self.gst_media_obj

    def get_timestamp(self):
        sample = self.get_sample()
        buf = sample.get_buffer()
        return buf.pts

    def _map_buffer(self):
        buf = self.sample.get_buffer()

        self._gst_memory_obj = buf.get_all_memory()
        ret, self.minfo = self._gst_memory_obj.map(self.map_flags)

        if ret is not True:
            return gst.FlowReturn.ERROR

        return gst.FlowReturn.OK

    def _unmap_buffer(self):
        self._gst_memory_obj.unmap(self.minfo)

    def __del__(self):
        self._unmap_buffer()
