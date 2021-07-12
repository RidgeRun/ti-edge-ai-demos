#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>
#  Based on Texas Instruments Incorporated - http://www.ti.com/


import logging
import numpy as np
import os
import sys
import yaml


def read_file(model_dir):
    try:
        with open(model_dir + "param.yaml", "r") as file:
            return yaml.safe_load(file)
    except OSError as e:
        logging.error("YAML file not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error("Error parsing file: %s" % (e))
        sys.exit(1)


class GetConfigYaml:
    """
    Class used to get parameters from a YAML file
    Parse the parameters for a YAML file with the TI Edge AI segmentation/detection/classification models
    Args:
        model_dir (string): The model directory
    """

    def __init__(self, model_dir):
        yaml_params = read_file(model_dir)
        self.params = self.parse_params(yaml_params, model_dir)

    def parse_params(self, yaml_params, model_dir):
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

        # metrics
        params.label_offset = 0
        if 'metric' in yaml_params:
            if 'label_offset_pred' in yaml_params['metric']:
                params.label_offset = yaml_params['metric']['label_offset_pred']

        return params
