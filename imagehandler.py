#!/usr/bin/env python

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

import cv2
import logging


class ImageHandler:
    def loadImage(self, image_name):
        try:
            return cv2.imread(image_name)
        except Exception as e:
            logging.warning("Unable to load the image")

    def saveImage(self, image_name, img):
        try:
            cv2.imwrite(image_name, img)
        except Exception as e:
            logging.warning("Unable to save the image")
