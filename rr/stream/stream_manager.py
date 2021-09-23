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

    def __call__(self, gst_image, gst_tensor):
        self.ai_manager.process_image(
            gst_image,
            gst_tensor,
            self.model,
            self.disp_width,
            self.disp_height)


class OnNewPrediction():
    def __init__(self, action_manager, display_manager):
        self.action_manager = action_manager
        self.display_manager = display_manager

    def __call__(self, prediction, image, media):
        self.display_manager.push_image(image, media)
        self.action_manager.execute(prediction, image, media)


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
            ai_manager_dict,
            display_manager,
            media_manager,
            model,
            disp_width,
            disp_height):
        """
        Constructor for the Stream Manager object
        """

        self.ai_manager_dict = ai_manager_dict

        self.media_manager = media_manager
        self.action_manager = action_manager
        self.display_manager = display_manager

        cb_prediction = OnNewPrediction(action_manager, display_manager)
        cb_image = {}
        for key in ai_manager_dict:
            on_new_image_cb = {key: OnNewImage(
                ai_manager_dict[key],
                model,
                disp_width,
                disp_height)}

            cb_image.update(on_new_image_cb)

            self.ai_manager_dict[key].install_callback(cb_prediction)

        self.media_manager.install_image_callback(cb_image)

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
            self.display_manager.stop_display()
            self.media_manager.stop_media()

        except Exception as e:
            raise StreamManagerError("Unable to stop the stream") from e
