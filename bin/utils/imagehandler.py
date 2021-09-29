#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import cv2
import logging
import numpy as np
import sys

default_dimentions = 3


class ImageHandler:
    """
    Constructor to create an image handler
    Handles file operations over images
    """

    def load_image(self, image_name):
        img = cv2.imread(image_name)

        if (not np.any(img)):
            logging.error("Unable to load the input image")
            sys.exit(1)
        else:
            return img

    def save_image(self, image_name, img):
        saved_img = cv2.imwrite(image_name, img)

        if (not saved_img):
            logging.error("Unable to save the image")
            sys.exit(1)
        else:
            return saved_img

    def resize_image(self, img, new_size):
        try:
            return cv2.resize(img, new_size, interpolation=cv2.INTER_LINEAR)
        except cv2.error as e:
            logging.error("Unable to resize image")
            sys.exit(1)

    def image_to_tensor(image, data_type=np.uint8):
        image_array = np.asarray(image)
        tensor = np.expand_dims(image_array, axis=0)
        tensor = tensor.astype(data_type)

        return tensor

    def buffer_to_np_array(data, width, height):
        img = np.ndarray(shape=(height, width, default_dimentions),
                         dtype=np.uint8,
                         buffer=data)

        return img

    def buffer_to_tensor(data, width, height):
        tensor = np.ndarray(shape=(1, height, width, default_dimentions),
                            dtype=np.float32,
                            buffer=data)

        return tensor
