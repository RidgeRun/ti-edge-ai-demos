#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import cv2
import numpy as np
import threading

from bin.utils.getconfig import GetConfigYaml
from bin.utils.imagehandler import ImageHandler
from rr.gstreamer.gst_media import GstImage
from rr.gstreamer.gst_media import GstUtils
from TI.postprocess import PostProcessDetection
from TI.preprocess import PreProcessDetection
from TI.runtimes import *


def format_inf_results(classname, inference_results):
    dict_instances = {}

    class_IDs, scores, bounding_boxes = inference_results

    keys = ["x", "y", "width", "height"]
    instances = []
    for i, score in enumerate(np.squeeze(scores, axis=0)):
        dict_labels = {}
        prob = scores[0][i]

        fieldnames = {
            'label': classname,
            'probability': prob
        }

        dict_labels.update({"labels": [fieldnames]})
        dict_labels.update({"bbox": dict(zip(keys, bounding_boxes[0][i]))})

        instances.append(dict_labels)

    dict_instances.update({"instances": instances})

    return dict_instances


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

        self._model_config = GetConfigYaml(model)

        self.preprocess_obj = PreProcessDetection(model)

        RunTime = eval(self.preprocess_obj.params.run_time)
        self.inference_obj = RunTime(self.preprocess_obj.params)

        self.postprocess_obj = PostProcessDetection(
            model, disp_width, disp_height)

        # Make a warmup run to start the engine
        self._model_channel_axis = self._model_config.params.data_layout.index(
            'C')

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

        img_preprocessed = self.preprocess_obj.get_preprocessed_image(image)

        return img_preprocessed

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

        results = self.inference_obj.run(image)

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

        img_postprocessed = self.postprocess_obj.get_postprocessed_image(
            image, results)

        return img_postprocessed

    def get_classname(self):
        return self.postprocess_obj.get_classname()


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

    def process_image(self, image, gst_tensor, model, disp_width, disp_height):
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

        # Run the inference
        tensor = ImageHandler.buffer_to_tensor(
            gst_tensor.get_data(),
            gst_tensor.get_data_layout(),
            gst_tensor.get_width(),
            gst_tensor.get_height())

        inference_results = self.run_inference(tensor)

        image_postprocessed = self.postprocess_detection(
            img, inference_results)

        # Create GstBuffer from postprocess image
        h, w, c = image_postprocessed.shape
        buffer = GstUtils.buffer_new_wrapped(image_postprocessed.tobytes())

        # Create GstImage
        sample = image.get_sample()
        caps = sample.get_caps()
        sample2 = GstUtils.sample_new(buffer, caps)
        image2 = GstImage(None, w, h, "RGB", sample2, image.get_media())

        classname = self.get_classname()
        inference_results2 = format_inf_results(classname, inference_results)

        self.on_new_prediction_cb_(
            inference_results2,
            image2,
            gst_media)
