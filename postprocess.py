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

(cam_width, cam_height) = (1280, 720)
(disp_width, disp_height) = (1920, 1080)


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


class PostProcessDetection(PostProcess):
    def overlay_bounding_box(frame, results, classnames, score_thresh,
                             scalex, scaley, label_offset, formatter):
        class_IDs, scores, bounding_boxes = results
        for i, score in enumerate(np.squeeze(scores, axis=0)):
            if (score <= score_thresh):
                continue
            box = bounding_boxes[0][i]
            box = [int(box[formatter.index(0)] * scalex),
                   int(box[formatter.index(1)] * scaley),
                   int(box[formatter.index(2)] * scalex),
                   int(box[formatter.index(3)] * scaley)]
            class_id = label_offset[int(class_IDs[0][i])]
            # print("%d: Detected object %s with score %f @(%d,%d) to (%d,%d)" % \
            # (i, classnames[class_id], score, box[0], box[1], box[2], box[3]))
            box_color = (int(120 * score), int(120 * score), int(50 * score))
            text_color = (int(240 * score), int(240 * score), int(240 * score))
            cv2.rectangle(frame, (box[0], box[1]),
                          (box[2], box[3]), box_color, 2)
            cv2.rectangle(frame,
                          (int((box[2] + box[0]) / 2) - 5,
                           int((box[3] + box[1]) / 2) + 5),
                          (int((box[2] + box[0]) / 2) + 160,
                              int((box[3] + box[1]) / 2) - 15),
                          box_color,
                          -1)
            cv2.putText(frame,
                        classnames[class_id],
                        (int((box[2] + box[0]) / 2),
                         int((box[3] + box[1]) / 2)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        text_color)

        return frame

    def get_preprocessed_image(self, img, results):
        classnames = eval(self.params.dataset)
        scalex = cam_width / self.params.resize[0]
        scaley = cam_height / self.params.resize[1]

        img = utils.overlay_bounding_box(
            img,
            results,
            classnames,
            args.threshold,
            scalex,
            scaley,
            params.label_offset,
            params.formatter)
        img = utils.overlay_title(img, disp_width - cam_width,
                                  disp_height - cam_height)
        return img


class PostProcessClassification(PostProcess):
    def overlay_top5_classnames(
            self,
            frame,
            results,
            classnames,
            label_offset):
        """
        Process the results of the image classification model and draw text
        describing top 5 detected objects on the image.

        Args:
            frame (numpy array): Input image in BGR format where the overlay should
        be drawn
        results (numpy array): Output of the model run
            classnames (dictionary): Map for class ID to class name
        """
        top5 = np.argpartition(results[0], -5)[0][:-6:-1]
        orig_width = frame.shape[1]
        orig_height = frame.shape[0]
        # cv2.rectangle(frame, (0, 0), (int(orig_width/4), int(orig_height/4)), \
        #                               (40, 40, 40), -1)
        cv2.putText(frame, "Top 5 detected classes:", (int(
            3 * orig_width / 4), 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        row = 1
        for idx in top5:
            cv2.putText(
                frame,
                "%s" %
                classnames.get(
                    idx +
                    label_offset),
                (int(
                    3 *
                    orig_width /
                    4),
                    40 +
                    40 *
                    row),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,
                 255,
                 255),
                2)
            row = row + 1

        end = time()
        return frame

    def get_postprocessed_image(self, img):
        classnames = eval(self.params.dataset)

        img = overlay_title(
            img,
            disp_width -
            cam_width,
            disp_height -
            cam_height)
        img = overlay_top5_classnames(
            img, results, classnames, self.params.label_offset)
