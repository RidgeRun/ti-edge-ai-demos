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

from getconfig import *


class PreProcess:
    def __init__(self, img, model_dir):
        # Get parsed the model params
        config = GetConfigYaml(model_dir)
        self.params = config.params

        # Get the image
        self.img = img

    def resize(self, img, new_width, new_height):
        img = cv2.resize(img, (new_width, new_height),
                         interpolation=cv2.INTER_LINEAR)

        return img

    def channel_swap_bgr_to_rgb(self, img):
        img = img[:, :, ::-1]

        return img

    def change_format(self, img, fin, fout):
        if (fin == 'HWC' and fout == 'NCHW'):
            transpose = (2, 0, 1)
            newdim = 0
        elif (fin == 'HWC' and fout == 'NHWC'):
            transpose = False
            newdim = 0
        elif (fin == 'NCHW' and fout == 'NHWC'):
            transpose = (0, 2, 3, 1)
        else:
            print("[ERROR] Unsupported format conversion from %s to %s" %
                  (fin, fout))
            return None

        if (transpose):
            img = np.transpose(img, transpose)
        if (newdim is not None):
            img = np.expand_dims(img, axis=newdim)
        img = img.astype(np.float32)

        return img

    def subtract_mean_and_scale(self, img, mean, scale, chan_axis):
        for mean, scale, ch in zip(mean, scale, range(img.shape[chan_axis])):
            if (chan_axis == 0):
                img[ch, :, :, :] = ((img[ch, :, :, :] - mean) * scale)
            elif (chan_axis == 1):
                img[:, ch, :, :] = ((img[:, ch, :, :] - mean) * scale)
            elif (chan_axis == 2):
                img[:, :, ch, :] = ((img[:, :, ch, :] - mean) * scale)
            elif (chan_axis == 3):
                img[:, :, :, ch] = ((img[:, :, :, ch] - mean) * scale)
            else:
                print("[ERROR] Unsupported channel axis")

        return img

    def get_preprocessed_image(self, img):
        img = self.resize(img, *self.params.resize)
        if (not self.params.reverse_channels):
            img = self.channel_swap_bgr_to_rgb(img)
        img = self.change_format(img, "HWC", self.params.data_layout)
        img = self.subtract_mean_and_scale(
            img,
            self.params.mean,
            self.params.scale,
            self.params.data_layout.index("C"))
        return img


class PreProcessDetection(PreProcess):
    def get_preprocessed_image(self, img):
        img = self.resize(img, *self.params.resize)
        if (not self.params.reverse_channels):
            img = self.channel_swap_bgr_to_rgb(img)
        img = self.change_format(img, 'HWC', self.params.data_layout)
        img = self.subtract_mean_and_scale(
            img,
            self.params.mean,
            self.params.scale,
            self.params.data_layout.index('C'))
        return img


class PreProcessClassification(PreProcess):
    def resize_smaller_dim(self, img, dim):
        orig_height, orig_width, _ = img.shape
        new_height = orig_height * dim // min(img.shape[:2])
        new_width = orig_width * dim // min(img.shape[:2])

        img = self.resize(img, new_width, new_height)

        return img

    def centre_crop(self, img, width, height):
        orig_height, orig_width, _ = img.shape
        startx = orig_width // 2 - (width // 2)
        starty = orig_height // 2 - (height // 2)

        img = img[starty: starty + height, startx: startx + width]

        return img

    def get_preprocessed_image(self, img):
        img = self.resize_smaller_dim(img, self.params.resize)
        img = self.centre_crop(img, *self.params.crop)
        if (not self.params.reverse_channels):
            img = self.channel_swap_bgr_to_rgb(img)
        img = self.change_format(img, 'HWC', self.params.data_layout)
        img = self.subtract_mean_and_scale(
            img,
            self.params.mean,
            self.params.scale,
            self.params.data_layout.index('C'))

        return img
