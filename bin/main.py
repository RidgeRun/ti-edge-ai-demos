#!/usr/bin/env python3

#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import argparse
from utils.imagehandler import *
from TI.postprocess import *
from TI.preprocess import *
from TI.runtimes import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        help="The path to the model directory that is going to be used",
        required=True)
    parser.add_argument(
        "-i",
        "--input",
        help="The path to the input image",
        required=True)
    parser.add_argument(
        "-o",
        "--output",
        help="The output image name",
        required=True)
    parser.add_argument(
        "--height",
        help="The display height",
        type=int,
        default=720)
    parser.add_argument(
        "--width",
        help="The display width",
        type=int,
        default=1280)

    args = parser.parse_args()

    return vars(args)


def main():
    args = parse_args()
    image_handler = ImageHandler()
    img = image_handler.load_image(args['input'])

    # Preprocess
    preprocess = PreProcessDetection(img, args['model'])
    img_preprocessed = preprocess.get_preprocessed_image(img)

    # Inference
    RunTime = eval(preprocess.params.run_time)
    run_time = RunTime(preprocess.params)
    results = run_time.run(img_preprocessed)

    # Postprocess
    (disp_width, disp_height) = (args['width'], args['height'])
    postprocess = PostProcessDetection(
        img, args['model'], *(disp_width, disp_height))
    img = postprocess.get_postprocessed_image(img, results)

    image_handler.save_image(args['output'], img)


if __name__ == "__main__":
    main()
