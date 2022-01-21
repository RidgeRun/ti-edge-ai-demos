#!/usr/bin/env python3

#  Copyright (C) 2021-2022 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#           Emmanuel Madrigal <emmanuel.madrigal@ridgerun.com>

import gi

from rr.gstreamer.gst_media import GstMedia, GstImage  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from bin.utils.getconfig import GetConfigYaml

image_appsink_name_base = "image_appsink"
tensor_appsink_name_base = "tensor_appsink"
SECONDS_TO_NANOSECONDS = 1e9


class GstAppSinkError(RuntimeError):
    pass


class GstAppSink(GstMedia):
    """
    Class that creates the GStreamer input preproc handler
    Attributes
    ----------
    _pipeline : GstElement
        A private GStreamer pipeline object

    """

    def __init__(self):
        """
        Constructor for the GStreamer appsink object
        """

        GstMedia.__init__(self)

        self._image_appsink_name = None
        self._tensor_appsink_name = None

    def install_image_callback(self, callback):
        if callback is None:
            raise GstAppSinkError("Invalid callback")

        self.image_callback = callback

    def install_buffer_callback(self):
        try:
            appsink = self._pipeline.get_by_name(self._image_appsink_name)
            appsink.connect("new-sample", self._on_new_buffer, appsink)

        except AttributeError as e:
            raise GstAppSinkError("Unable to install buffer callback") from e

    def set_triggers(self, triggers):
        self._triggers = triggers

    def get_triggers(self):
        return self._triggers

    def _on_new_buffer(self, appsink, data):
        sample = appsink.emit("pull-sample")

        caps = sample.get_caps()
        width, height, format = (caps.get_structure(0).get_value("width"),
                                 caps.get_structure(0).get_value("height"),
                                 caps.get_structure(0).get_value("format")
                                 )

        gst_image = GstImage(
            width,
            height,
            format,
            sample,
            self)

        # Bind the tensor pull
        tensor_appsink = self._pipeline.get_by_name(self._tensor_appsink_name)
        tensor_sample = tensor_appsink.emit("pull-sample")

        tensor_caps = tensor_sample.get_caps()
        tensor_width = tensor_caps.get_structure(0).get_value("tensor-width")
        tensor_height = tensor_caps.get_structure(0).get_value("tensor-height")
        tensor_format = tensor_caps.get_structure(0).get_value("tensor-format")

        gst_tensor = GstImage(
            tensor_width,
            tensor_height,
            tensor_format,
            tensor_sample,
            self)

        self.image_callback(gst_image, gst_tensor)

        return gst.FlowReturn.OK

    @classmethod
    def make(cls, desc, all_triggers):
        image_name = image_appsink_name_base + "_" + desc["id"]
        tensor_name = tensor_appsink_name_base + "_" + desc["id"]

        pipe = '''
                interpipesrc listen-to={} ! appsink sync=true async=false max-buffers=2 qos=false emit-signals=true drop=true name={}
                interpipesrc listen-to={} ! appsink sync=true async=false max-buffers=2 qos=false emit-signals=true drop=true name={}
               '''.format("image_" + desc["id"],
                          image_name,
                          "tensor_" + desc["id"],
                          tensor_name)

        media = GstAppSink()
        media.create_media(desc['id'], pipe)
        media._image_appsink_name = image_name
        media._tensor_appsink_name = tensor_name

        media_triggers = []
        for trigger in desc['triggers']:
            match = next(
                (candidate for candidate in all_triggers if trigger == candidate.get_name()),
                None)
            if not match:
                raise GstAppSinkError(
                    "Unknown trigger '%s', corrupted description" %
                    trigger)
            media_triggers.append(match)

        media.set_triggers(media_triggers)

        return media

    def play_media(self):
        """Set the media state to playing
        Raises
        ------
        GstMediaError
            If couldn't set the media state to playing
        """

        GstMedia.play_media(self)

        # Install the buffer callback that passes the image media to a client
        if self.image_callback is not None:
            self.install_buffer_callback()
