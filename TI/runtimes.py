#!/usr/bin/env python3

#  Copyright (C) 2021 Texas Instruments Incorporated - http://www.ti.com/
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#    Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#    Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
#
#    Neither the name of Texas Instruments Incorporated nor the names of
#    its contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from dlr import DLRModel
import numpy as np
import tflite_runtime.interpreter as tflitert_interpreter


class tvmdlr:
    '''
    Abstracts the tvmdlr Run Time
    '''

    def __init__(self, params):
        self.params = params
        self.model = DLRModel(params.artifacts, 'cpu')
        self.input_names = self.model.get_input_names()

    def run(self, input_img):
        return self.model.run({self.input_names[0]: input_img})


class tflitert:
    '''
    Abstracts the tflitert Run Time
    '''

    def __init__(self, params):
        self.params = params
        delegate_options = {
            "tidl_tools_path": "null",
            "artifacts_folder": params.artifacts,
            "import": 'no',
        }

        try:
            tidl_delegate = [
                tflitert_interpreter.load_delegate(
                    '/usr/lib/libtidl_tfl_delegate.so',
                    delegate_options)]
        except ValueError as e:
            logging.error("Delegate library not found")
            sys.exit(1)

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
