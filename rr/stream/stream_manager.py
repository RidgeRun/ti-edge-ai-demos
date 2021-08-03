#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from rr.ai.ai_manager import AIManagerOnNewImage
from rr.gstreamer.media_manager import MediaManager

model = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"
disp_width = 2040
disp_height = 1920


class OnNewImage():
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager

    def __call__(self, image):
        self.ai_manager.process_image(image, model, disp_width, disp_height)


class StreamManagerError(RuntimeError):
    pass


class StreamManager():
    """
    Class that orchestrate the stream interoperations

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self, ai_manager, media_manager):
        """
        Constructor for the Stream Manager object
        """

        self.ai_manager = ai_manager
        self.media_manager = media_manager

        on_new_image_cb = OnNewImage(self.ai_manager)

        self.media_manager.push_buffer(on_new_image_cb)
