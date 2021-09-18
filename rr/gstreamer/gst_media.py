#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import gi  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from bin.utils.getconfig import GetConfigYaml

model = '/opt/model_zoo/TFL-OD-2000-ssd-mobV1-coco-mlperf-300x300/'
image_appsink_name = "image_appsink"
tensor_appsink_name = "tensor_appsink"


class GstMediaError(RuntimeError):
    pass


class GstMedia():
    """
    Class that creates the GStreamer handler
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
    """

    def __init__(self):
        """
        Constructor for the Media Gstreamer Manager object
        """

        gst.init(None)

        self._name = None
        self._pipeline = None
        self.image_callback = None
        self.tensor_callback = None
        self.callback_sample = None
        self._triggers = []

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

        ret = self._pipeline.set_state(gst.State.PLAYING)
        if gst.StateChangeReturn.FAILURE == ret:
            raise GstMediaError("Unable to play the media")

        # Install the buffer callback that passes the image media to a client
        if self.image_callback is not None:
            self.install_buffer_callback()

        # Install the callback that passes the new tensor from the AppSink to a
        # client
        if self.tensor_callback is not None:
            self.install_tensor_buffer_callback()

    def stop_media(self):
        """Set the media state to stopped
        Raises
        ------
        GstMediaError
            If couldn't set the media state to stopped
        """

        # Nothing to be done if the pipe is not running
        ret, current, pending = self._pipeline.get_state(gst.CLOCK_TIME_NONE)
        if current != gst.State.PLAYING:
            return

        # Send an EOS and wait 5 seconds for the EOS to arrive before closing
        timeout = 5000000000  # 5 seconds in nanoseconds
        self._pipeline.send_event(gst.Event.new_eos())
        self._pipeline.get_bus().timed_pop_filtered(timeout, gst.MessageType.EOS)

        ret = self._pipeline.set_state(gst.State.NULL)
        if gst.StateChangeReturn.FAILURE == ret:
            raise GstMediaError("Unable to stop the media")

    def install_image_callback(self, callback):
        if callback is None:
            raise GstMediaError("Invalid callback")

        self.image_callback = callback

    def install_buffer_callback(self):
        try:
            appsink = self._pipeline.get_by_name(image_appsink_name)
            appsink.connect("new-sample", self._on_new_buffer, appsink)

        except AttributeError as e:
            raise GstMediaError("Unable to install buffer callback") from e

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

        self.image_callback(gst_image)

        return gst.FlowReturn.OK

    def install_tensor_callback(self, callback):
        if callback is None:
            raise GstMediaError("Invalid callback")

        self.tensor_callback = callback

    def install_tensor_buffer_callback(self):
        try:
            appsink = self._pipeline.get_by_name(tensor_appsink_name)
            appsink.connect("new-sample", self._on_new_tensor, appsink)

        except AttributeError as e:
            raise GstMediaError("Unable to install tensor callback") from e

    def _on_new_tensor(self, appsink, data):
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

        self.tensor_callback(gst_image)

        return gst.FlowReturn.OK

    def get_name(self):
        """Getter for the private media name
        """
        return self._name

    def get_media(self):
        """Getter for the private media object
        """
        return self._pipeline

    def set_triggers(self, triggers):
        self._triggers = triggers

    def get_triggers(self):
        return self._triggers

    @classmethod
    def make(cls, desc, all_triggers):
        # Parse parameters from model
        model_config = GetConfigYaml(model)

        model_resize = model_config.params.resize
        model_mean = model_config.params.mean
        model_scale = model_config.params.scale
        model_channel_format = model_config.params.data_layout
        model_channel_axis = model_config.params.data_layout.index('C')

        pipe = '''uridecodebin uri=%s caps=video/x-h264 ! queue ! h264parse ! v4l2h264dec capture-io-mode=5 ! video/x-raw,format=NV12 !
                  tiovxmultiscaler src_0::pool-size=16 sink::pool-size=16 ! tiovxcolorconvert in-pool-size=16 out-pool-size=16 ! video/x-raw,width=320,height=240,format=RGB ! tee name=t
                  t. ! queue ! appsink sync=true async=false max-buffers=3 qos=false emit-signals=true drop=true name=%s
                  t. ! queue ! videoscale ! video/x-raw,width=%s,height=%s,format=RGB !
                               tiovxdlpreproc mean-0=%s mean-1=%s mean-2=%s scale-0=%s scale-1=%s scale-2=%s data-type=10 channel-order=1 tensor-format=0 ! application/x-tensor-tiovx !
                               appsink sync=true async=false max-buffers=3 qos=false emit-signals=true drop=true name=%s''' % (desc["uri"],
                                                                                                                               image_appsink_name,
                                                                                                                               *(model_resize),
                                                                                                                               *(model_mean),
                                                                                                                               *(model_scale),
                                                                                                                               tensor_appsink_name)
        media = GstMedia()
        media.create_media(desc['id'], pipe)

        media_triggers = []
        for trigger in desc['triggers']:
            match = next(
                (candidate for candidate in all_triggers if trigger == candidate.get_name()),
                None)
            if not match:
                raise GstMediaError(
                    "Unknown trigger '%s', corrupted description" %
                    trigger)
            media_triggers.append(match)

        media.set_triggers(media_triggers)

        return media


class GstImage():
    def __init__(self, width, height, format, sample, gst_media_obj):
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


class GstUtils():
    def __init__(self):
        pass

    def buffer_new_wrapped(data):
        return gst.Buffer.new_wrapped(data)

    def buffer_new_wrapped_full(data, size):
        return gst.Buffer.new_wrapped_full(0, data, size, 0, None, None)

    def sample_new(buffer, caps):
        return gst.Sample.new(buffer, caps, None, None)
