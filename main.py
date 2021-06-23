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

from imagehandler import *
from preprocess import *
from postprocess import *
from runtimes import *

model_dir = "/opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/"


def main():
    image_handler = ImageHandler()
    img = image_handler.loadImage("linux.jpg")

    preprocess = PreProcessDetection(img, model_dir)
    img = preprocess.get_preprocessed_image(img)
    RunTime = eval(preprocess.params.run_time)
    run_time = RunTime(preprocess.params)
    results = run_time.run(img)
    postprocess = PostProcessDetection(img, model_dir)
    img = get_postprocessed_image(img, results)

    image_handler.saveImage("linux_preprocessed.jpg", img)


if __name__ == "__main__":
    main()
