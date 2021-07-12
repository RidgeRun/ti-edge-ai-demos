#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import cv2
import logging
import numpy as np
import sys


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
        try:
            cv2.imwrite(image_name, img)
        except cv2.error as e:
            logging.error("Unable to save image")
            sys.exit(1)

    def resize_image(self, img, new_size):
        try:
            return cv2.resize(img, new_size, interpolation=cv2.INTER_LINEAR)
        except cv2.error as e:
            logging.error("Unable to resize image")
            sys.exit(1)
