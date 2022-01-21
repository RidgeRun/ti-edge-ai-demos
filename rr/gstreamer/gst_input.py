#!/usr/bin/env python3

#  Copyright (C) 2022 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#           Emmanuel Madrigal <emmanuel.madrigal@ridgerun.com>

from typing import List

from rr.gstreamer.gst_stream import GstStream
from rr.gstreamer.gst_appsink import GstAppSink


class GstInput:
    def __init__(self, stream: GstStream, appsink: List[GstAppSink]):
        self.stream = stream
        self.appsink = appsink
