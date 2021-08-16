#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from threading import Timer, Lock

from rr.actions.gst_recording_media import GstRecordingMedia


class RecordingMedia():
    def __init__(self, rec_media, recording, timer):
        self.rec_media = rec_media
        self.is_recording = recording
        self.timer = timer

    def __del__(self):
        if self.is_recording:
            self.timer.cancel()
            self.rec_media.stop_media()


class RecordEvent():
    def __init__(self, name, rec_dir):
        self._name = name
        self._rec_dir = rec_dir
        self._medias_dict = {}
        self._mutex = Lock()

    def get_name(self):
        return self._name

    def execute(self, media, image, rec_time, inf_filter):
        media_name = media.get_name()

        self._mutex.acquire()

        self._check_dict(media_name)
        media = self._medias_dict[media_name]

        if inf_filter.is_triggered():

            if not media.is_recording:
                timestamp = image.get_timestamp()
                filename = self._rec_dir + "/" + "detection_recording_" + \
                    media_name + "_" + timestamp + ".ts"
                self._medias_dict[media_name].rec_media = GstRecordingMedia(
                    filename)

            self._start_timer(media_name, rec_time, inf_filter)

        if media.is_recording:
            media.rec_media.push_image(image)

        self._mutex.release()

    def _start_timer(self, media_name, rec_time, inf_filter):
        media = self._medias_dict[media_name]

        if media.is_recording:
            media.timer.cancel()

        media.timer = Timer(rec_time, self._stop_recording, [media_name])
        media.is_recording = True

        media.timer.start()

    def _check_dict(self, media_name):
        if media_name not in self._medias_dict:
            self._medias_dict[media_name] = RecordingMedia(None, False, None)

    def _stop_recording(self, media_name):
        self._mutex.acquire()
        self._medias_dict[media_name].rec_media.stop_media()
        self._medias_dict[media_name].is_recording = False
        self._mutex.release()

    def stop_recordings(self):
        for media in list(self._medias_dict):
            del self._medias_dict[media]

    @classmethod
    def make(cls, desc):
        try:
            name = desc["name"]
            location = desc["location"]
        except KeyError as e:
            raise RecordEventError("Malformed record event description") from e

        return RecordEvent(name, location)
