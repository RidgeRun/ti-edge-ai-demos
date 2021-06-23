#!/usr/bin/env python3

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

import yaml
import cv2
import numpy as np


class PostProcess:
    def __init__(self, img, model_dir):
        # Get parsed the model params
        self.params = GetConfigYaml(model_dir)

        # Get the image
        self.img = img

        # Get the model and demo names
        self.model_name = model_dir[:len(model_dir) - 1]
        self.demo_name = 'Simple example'

    def overlay_title(self, img):
        (cam_width, cam_height) = (1280, 720)
        (disp_width, disp_height) = (1920, 1080)

        padx = disp_width - cam_width
        pady = disp_height - cam_height

        img = cv2.copyMakeBorder(img,
                                 int(pady / 2),
                                 pady - int(pady / 2),
                                 int(padx / 2),
                                 padx - int(padx / 2),
                                 cv2.BORDER_CONSTANT)
        img = cv2.putText(img, "Texas Instruments - Edge Analytics", (40, 40),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        img = cv2.putText(img, self.demo_name, (40, 40 + 50),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        img = cv2.putText(img, "model : " + self.model_name, (40, 40 + 100),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img
