#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import cv2
import numpy as np
import random
import unittest
from unittest.mock import MagicMock

from TI.postprocess import PostProcessDetection
from TI.preprocess import PreProcessDetection
from rr.ai.ai_manager import AIManager
from rr.ai.ai_manager import AIManagerError
from rr.ai.ai_manager import AIManagerOnNewImage
from rr.config.app_config_loader import AppConfigLoader
from rr.gstreamer.gst_media import GstImage
from rr.gstreamer.gst_media import GstMedia
from rr.gstreamer.gst_media import GstUtils
from bin.utils.getconfig import GetConfigYaml
from bin.utils.imagehandler import ImageHandler


default_config_file = "tests/test_config.yaml"
width = 1920
height = 1080
color = (100, 100, 100)
disp_width = 2040
disp_height = 1920
img_path = "./data/0004.jpg"


class MockImage():
    def __init__(self, width, height, color):
        img_handler = ImageHandler()

        self.mock_img = self._create_img(width, height, rgb_color=color)
        self.real_img = img_handler.load_image(img_path)

    def _create_img(self, width, height, rgb_color=(0, 0, 0)):
        img = np.zeros((height, width, 3), np.uint8)

        color = tuple(reversed(rgb_color))
        img[:] = color

        return img

    def get_image(self):
        return self.real_img


class TestAIManager(unittest.TestCase):
    def setUp(self):
        global width, height, color

        config_obj = AppConfigLoader()
        config_dict = config_obj.load(default_config_file)
        model_params = config_dict['model_params']

        self.model = model_params['model']['detection']
        self.disp_width = model_params['disp_width']
        self.disp_height = model_params['disp_height']

        self.mock_image = MockImage(width, height, color)
        self.img = self.mock_image.get_image()

        self.ai_manager = AIManager(
            self.model,
            self.disp_width,
            self.disp_height)

    def testpreprocess_detection(self):
        img = self.ai_manager.preprocess_detection(self.img)
        self.assertTrue(0 != img.size)

    def testruntime(self):
        preprocess = PreProcessDetection(self.model)
        img = self.ai_manager.preprocess_detection(self.img)

        results = self.ai_manager.run_inference(img)

    def testpostprocess_detection(self):
        preprocess = PreProcessDetection(self.model)
        img = self.ai_manager.preprocess_detection(self.img)
        results = self.ai_manager.run_inference(img)

        postprocess = PostProcessDetection(
            self.model, self.disp_width, self.disp_height)
        img = postprocess.get_postprocessed_image(self.img, results)
        self.assertTrue(0 != img.size)


class TestAIManagerOnNewImage(unittest.TestCase):
    def setUp(self):
        global width, height, color

        config_obj = AppConfigLoader()
        config_dict = config_obj.load(default_config_file)
        model_params = config_dict['model_params']

        self.model = model_params['model']['detection']
        self.disp_width = model_params['disp_width']
        self.disp_height = model_params['disp_height']

        # Parse info from AI model
        _ai_model_config = GetConfigYaml(self.model)
        self.ai_model_resize = _ai_model_config.params.resize
        self.ai_model_resize_w, self.ai_model_resize_h = tuple(
            self.ai_model_resize)

        self.mock_image = MockImage(width, height, color)
        self.img = self.mock_image.get_image()

        self.ai_manager = AIManagerOnNewImage(
            self.model,
            self.disp_width,
            self.disp_height)

    def testprocess_image(self):
        h, w, c = self.img.shape
        size = h * w * c

        image = MagicMock()
        image.get_data = MagicMock(return_value=self.img)
        image.get_width = MagicMock(return_value=w)
        image.get_height = MagicMock(return_value=h)

        gst_tensor = MagicMock()
        img_resized = cv2.resize(
            self.img,
            tuple(
                self.ai_model_resize),
            interpolation=cv2.INTER_LINEAR)
        tensor = ImageHandler.image_to_tensor(img_resized, np.float32)

        gst_tensor.get_data = MagicMock(return_value=tensor.tobytes())
        gst_tensor.get_width = MagicMock(return_value=self.ai_model_resize_w)
        gst_tensor.get_height = MagicMock(return_value=self.ai_model_resize_h)

        gst_media_obj = GstMedia()
        desc = "videotestsrc is-live=true ! fakesink async=false"
        gst_media_obj.create_media("name", desc)
        gst_media_obj.play_media()
        image.get_media = MagicMock(return_value=gst_media_obj)

        buf = GstUtils.buffer_new_wrapped_full(self.img.tobytes(), size)
        sample = GstUtils.sample_new(buf, None)
        image.get_sample = MagicMock(return_value=sample)

        cb = MagicMock(None, self.img, gst_media_obj)
        self.ai_manager.install_callback(cb)
        self.ai_manager.process_image(
            image, gst_tensor, self.model, self.disp_width, self.disp_height)


if __name__ == '__main__':
    unittest.main()
