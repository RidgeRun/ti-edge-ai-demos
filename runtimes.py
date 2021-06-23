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


import tflite_runtime.interpreter as tflitert_interpreter
from dlr import DLRModel
import numpy as np


class tvmdlr:
    def __init__(self, params):
        self.params = params
        self.model = DLRModel(params.artifacts, 'cpu')
        self.input_names = self.model.get_input_names()

    def run(self, input_img):
        return self.model.run({self.input_names[0]: input_img})


class tflitert:
    def __init__(self, params):
        self.params = params
        delegate_options = {
            "tidl_tools_path": "null",
            "artifacts_folder": params.artifacts,
            "import": 'no',
        }
        tidl_delegate = [
            tflitert_interpreter.load_delegate(
                '/usr/lib/libtidl_tfl_delegate.so',
                delegate_options)]
        self.interpreter = tflitert_interpreter.Interpreter(
            params.model_path, experimental_delegates=tidl_delegate)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def run(self, input_img):
        if (self.input_details[0]['dtype'] != np.float32):
            input_img = np.uint8(input_img)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_img)
        self.interpreter.invoke()
        results = [self.interpreter.get_tensor(output_detail['index'])
                   for output_detail in self.output_details]
        if (self.params.task_type == 'detection'):
            return self._shuffle_detection_results(results, input_img.shape[2])
        else:
            return results

    def _shuffle_detection_results(self, results, scale):
        bounding_boxes, class_IDs, scores, size = results
        return (class_IDs[:, 0:int(size[0])], scores[:, 0:int(size[0])],
                bounding_boxes[:, 0:int(size[0])] * scale)
