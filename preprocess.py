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

import yaml
import cv2
import numpy as np


class PreProcess:
    def __init__(self, img, model_dir):
        with open(model_dir + 'param.yaml', 'r') as f:
            params = yaml.safe_load(f)

        self.img = img

        # preprocess params
        self.resize = params['preprocess']['resize']
        crop = params['preprocess']['crop']
        if (type(crop) == int):
            self.crop = (crop, crop)
        self.mean = params['preprocess']['mean']
        self.scale = params['preprocess']['scale']
        self.reverse_channels = params['preprocess']['reverse_channels']
        self.data_layout = params['preprocess']['data_layout']

    def resize(self, img, new_width, new_height):
        img = cv2.resize(img, (new_width, new_height),
                         interpolation=cv2.INTER_LINEAR)

        return img

    def channel_swap_bgr_to_rgb(self, img):
        img = img[:, :, ::-1]

        return img

    def change_format(self, img, fin, fout):

    def subtract_mean_and_scale(self, img, mean, scale, chan_axis):
