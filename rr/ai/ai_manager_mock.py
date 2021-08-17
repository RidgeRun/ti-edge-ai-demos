#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from bin.utils.imagehandler import ImageHandler
from rr.gstreamer.gst_media import GstImage
from rr.gstreamer.gst_media import GstUtils


class AIManagerError(RuntimeError):
    pass


class AIManager():
    """
    Class that handles the AI modules

    Attributes
    ----------
    preprocess_obj : PreProcessDetection object
        The PreProcessDetection object

    preprocess_obj : PreProcessDetection object
        The PreProcessDetection object

    Methods
    -------
    preprocess_detection(image : image input)
        Preprocess the image according to the model

    run_inference(image : image input):
        Apply inference to the image

    postprocess_detection(image : image input, results : run_inference return):
        Postprocess the image according to the inference results
    """

    def __init__(
            self,
            model,
            disp_width,
            disp_height):
        """
        Constructor for the AI Manager object
        """

    def preprocess_detection(self, image):
        """Preprocess the image

        Parameters
        ----------
        image : image input
            The image to preprocess

        Raises
        ------
        AIManagerError
            If couldn't preprocess the image
        """

        return image

    def run_inference(self, image):
        """Apply inference to the image

        Parameters
        ----------
        image : image input
            The image to preprocess

        inference_model : str
            The inference model to apply

        preprocess : AI Preprocess object
            The AI Preprocess object

        Raises
        ------
        AIManagerError
            If couldn't run the inference to the image
        """

        results = {
            'instances': [
                {
                    'labels': [
                        {
                            'label': 'male',
                            'probability': 0.9

                        },
                        {
                            'label': 'Label1.2',
                            'probability': 0.1
                        }
                    ],
                    'bbox': {
                        'x': 0,
                        'y': 1,
                        'width': 2,
                        'height': 3
                    }
                },
                {
                    'labels': [
                        {
                            'label': 'Label2.1',
                            'probability': 0.2
                        },
                        {
                            'label': 'Label2.2',
                            'probability': 0.8,
                        }
                    ],
                    'bbox': {
                        'x': 0,
                        'y': 1,
                        'width': 2,
                        'height': 3
                    }
                },
            ]
        }

        return results

    def postprocess_detection(self, image, results):
        """Postprocess the image

        Parameters
        ----------
        image : image input
            The image to postprocess

        inference_model : str
            The inference model to apply

        Raises
        ------
        AIManagerError
            If couldn't postprocess the image
        """

        return image


class AIManagerOnNewImage(AIManager):
    """
    Class that performs the AI processing

    Attributes
    ----------

    Methods
    -------

    """

    def __init__(
            self,
            model,
            disp_width,
            disp_height):

        super().__init__(model, disp_width, disp_height)

        self.on_new_prediction_cb_ = None

    def install_callback(self, on_new_prediction_cb_):
        self.on_new_prediction_cb_ = on_new_prediction_cb_

    def process_image(self, image, model, disp_width, disp_height):
        """Get a image input

        Parameters
        ----------
        callback: function
            The callback function to receive the image

        Raises
        ------
        AIManagerError
            If couldn't get the image
        """

        gst_media = image.get_media()

        img = ImageHandler.buffer_to_np_array(
            image.get_data(), image.get_width(), image.get_height())

        image_preprocessed = self.preprocess_detection(img)

        inference_results = self.run_inference(image_preprocessed)

        image_postprocessed = self.postprocess_detection(
            img, inference_results)

        # Create GstBuffer from postprocess image
        h, w, c = image_postprocessed.shape
        size = h * w * c
        buffer = GstUtils.buffer_new_wrapped_full(
            image_postprocessed.tobytes(), size)

        # Create GstImage
        sample = image.get_sample()
        caps = sample.get_caps()
        sample2 = GstUtils.sample_new(buffer, caps)
        fmt = 'RGB'
        image2 = GstImage(w, h, fmt, sample2, image.get_media())

        self.on_new_prediction_cb_(
            inference_results,
            image,
            gst_media)
