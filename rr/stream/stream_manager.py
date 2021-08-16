#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from rr.ai.ai_manager import AIManagerOnNewImage
from rr.gstreamer.media_manager import MediaManager


class OnNewImage():
    def __init__(self, ai_manager, model, disp_width, disp_height):
        self.ai_manager = ai_manager
        self.model = model
        self.disp_width = disp_width
        self.disp_height = disp_height

    def __call__(self, image):
        self.ai_manager.process_image(
            image, self.model, self.disp_width, self.disp_height)


class OnNewPrediction():
    def __init__(self, action_manager, display_manager):
        self.action_manager = action_manager
        self.display_manager = display_manager

    def __call__(self, prediction, image, media):
        self.action_manager.execute(prediction, image, media)
        self.display_manager.push_image(image, media)


class StreamManagerError(RuntimeError):
    pass


class StreamManager():
    """
    Class that orchestrates the stream interoperations

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(
            self,
            action_manager,
            ai_manager,
            display_manager,
            media_manager,
            model,
            disp_width,
            disp_height):
        """
        Constructor for the Stream Manager object
        """

        self.ai_manager = ai_manager
        self.media_manager = media_manager
        self.action_manager = action_manager
        self.display_manager = display_manager

        cb = OnNewImage(ai_manager, model, disp_width, disp_height)
        self.media_manager.install_callback(cb)

        cb_prediction = OnNewPrediction(action_manager, display_manager)
        self.ai_manager.install_callback(cb_prediction)

    def play(self):
        """
        Start the stream server
        """

        try:
            self.display_manager.play_display()
            self.media_manager.play_media()

        except Exception as e:
            raise StreamManagerError("Unable to play the stream") from e

    def stop(self):
        """
        Stop the stream server
        """

        try:
            self.media_manager.stop_media()
            self.display_manager.stop_display()

        except Exception as e:
            raise StreamManagerError("Unable to stop the stream") from e
