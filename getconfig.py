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

import cv2
import logging
import yaml


class GetConfigYaml:
    def __init__(self, model_dir):
        yaml_params = self.read_file(model_dir)
        self.params = self.parse_params(yaml_params)

    def read_file(self, model_dir):
        with open(model_dir + "param.yaml", "r") as file:
            return yaml.safe_load(file)

    def parse_params(self, yaml_params):
        def params(): return None

        # Get the preprocess parameters
        params.resize = yaml_params['preprocess']['resize']
        crop = yaml_params['preprocess']['crop']
        if (isinstance(crop, int)):
            params.crop = (crop, crop)

        params.mean = yaml_params['preprocess']['mean']
        params.scale = yaml_params['preprocess']['scale']
        params.reverse_channels = yaml_params['preprocess']['reverse_channels']
        params.data_layout = yaml_params['preprocess']['data_layout']

        # Get the session parameters
        params.run_time = yaml_params['session']['session_name']
        if isinstance(yaml_params['session']['model_path'], list):
            params.model_path = model_dir + \
                yaml_params['session']['model_path'][0]
        else:
            params.model_path = model_dir + \
                yaml_params['session']['model_path']
        params.artifacts = model_dir + \
            yaml_params['session']['artifacts_folder']

        # Get the postprocess parameters
        params.formatter = (0, 1, 2, 3)
        if 'formatter' in yaml_params['postprocess']:
            formatter = yaml_params['postprocess']['formatter']
            if (formatter is not None):
                params.formatter = formatter['src_indices']

        # Get the dataset parameters
        params.dataset = yaml_params['input_dataset']['name']
        params.task_type = yaml_params['task_type']

        return params
