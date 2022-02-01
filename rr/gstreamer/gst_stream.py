#!/usr/bin/env python3

#  Copyright (C) 2021-2022 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#           Emmanuel Madrigal <emmanuel.madrigal@ridgerun.com>

import gi
from typing import List

from rr.gstreamer.gst_media import GstMedia  # nopep8
gi.require_version('Gst', '1.0')  # nopep8
gi.require_version('GLib', '2.0')  # nopep8
from gi.repository import Gst as gst  # nopep8
from gi.repository import GLib  # nopep8

from bin.utils.getconfig import GetConfigYaml
from rr.gstreamer.gst_media import GstMedia


class GstStreamError(RuntimeError):
    pass


class GstStream(GstMedia):
    """
    Class that creates the GStreamer input Stream handler
    Attributes
    ----------
    _pipeline : GstElement
        A private GStreamer pipeline object

    """

    def __init__(self):
        """
        Constructor for the GStreamer input Stream object
        """

        GstMedia.__init__(self)

    @classmethod
    def make(cls, descriptions, configs):
        # Parse parameters from model
        model_resize_w, model_resize_h = configs.ai_model.params.resize
        model_mean_0, model_mean_1, model_mean_2 = configs.ai_model.params.mean
        model_scale_0, model_scale_1, model_scale_2 = configs.ai_model.params.scale
        model_channel_format = configs.ai_model.params.data_layout

        pipe_str = '''tiovxmux name=image_mux sink_0::pool-size={sink_pool_size} sink_1::pool-size={sink_pool_size} sink_2::pool-size={sink_pool_size} sink_3::pool-size={sink_pool_size} sink_4::pool-size={sink_pool_size} sink_5::pool-size={sink_pool_size}
        tiovxmux name=tensor_mux sink_0::pool-size={sink_pool_size} sink_1::pool-size={sink_pool_size} sink_2::pool-size={sink_pool_size} sink_3::pool-size={sink_pool_size} sink_4::pool-size={sink_pool_size} sink_5::pool-size={sink_pool_size}
        tiovxdemux name=image_demux  sink::pool-size={sink_pool_size}
        tiovxdemux name=tensor_demux  sink::pool-size={sink_pool_size}'''.format(sink_pool_size=16)

        for i, desc in enumerate(descriptions):
            pipe_str += '''
              souphttpsrc timeout=0  location={uri} ! queue max-size-buffers=5 ! qtdemux ! h264parse ! v4l2h264dec capture-io-mode=5 ! video/x-raw,format=NV12 ! identity name=eos_{id} ! perf name=input_{id} !  tiovxmultiscaler target=VPAC_MSC{vpac_msc_id} name=multi_{id} sink::pool-size=5 src_0::pool-size=4 src_0::pool-size=4
              multi_{id}.src_0 ! queue max-size-buffers=5 leaky=2 ! video/x-raw,width={width},height={height} ! image_mux.
              multi_{id}.src_1 ! queue max-size-buffers=5 leaky=2 ! video/x-raw,width={width},height={height} ! tensor_mux.'''.format(
                width=model_resize_w,
                height=model_resize_h,
                uri=desc["uri"],
                id=desc["id"],
                vpac_msc_id= ((i % 2) + 1))

        pipe_str += '''
                image_mux. ! tiovxcolorconvert target=DSP-1  in-pool-size=2 out-pool-size=4 ! video/x-raw(memory:batched),format=RGB ! perf name=perf_image ! image_demux.'''.format(
            width=model_resize_w,
            height=model_resize_h)

        pipe_str += '''
                tensor_mux. ! tiovxdlpreproc target=DSP-2  in-pool-size=4 out-pool-size=4 qos=false mean-0={mean_0} mean-1={mean_1} mean-2={mean_2} scale-0={scale_0} scale-1={scale_1} scale-2={scale_2} data-type=float32 channel-order={channel_order} tensor-format=rgb ! perf name=perf_tensor ! tensor_demux.'''.format(
            width=model_resize_w,
            height=model_resize_h,
            mean_0=model_mean_0,
            mean_1=model_mean_1,
            mean_2=model_mean_2,
            scale_0=model_scale_0,
            scale_1=model_scale_1,
            scale_2=model_scale_2,
            channel_order=model_channel_format.lower())

        output_names = []
        for desc in descriptions:
            image_output = "image_" + desc["id"]
            tensor_output = "tensor_" + desc["id"]
            pipe_str += '''
                image_demux. ! queue max-size-buffers=5 leaky=2 ! interpipesink name={}'''.format(image_output)
            pipe_str += '''
                tensor_demux. ! queue max-size-buffers=5 leaky=2 ! interpipesink name={}'''.format(tensor_output)

            output_names.append((image_output, tensor_output))

        media = GstStream()
        media._output_name = output_names
        media.create_media("stream", pipe_str)

        return media
