#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import csv
import threading


class LogEventError(RuntimeError):
    pass


def open_file(path):
    """ Validates and opens a file from the given path

    Parameters
    ----------
    path : str
        The path to the logging file
    """
    try:
        return open(path, 'a', newline='')
    except Exception as e:
        raise LogEventError(
            "Unable to open logging events file for writing") from e


def find_max_probability(labels):
    """ Finds the label with the highest probability

    Parameters
    ----------
    labels : list
        A list with the inference result labels
    """

    first_label = labels[0]
    label_max_prob = first_label
    for label in labels:
        if label['probability'] > label_max_prob['probability']:
            label_max_prob = label
    return label_max_prob


def init_writer(log_file, headers):
    """ Sets the headers for the logging file

    Parameters
    ----------
    log_file : stream
        An open stream to write the headers to
    headers : List(str)
        A list of strings containing the headers to write
    """

    csv_writer = csv.DictWriter(log_file, fieldnames=headers)
    csv_writer.writeheader()

    return csv_writer


class LogEvent():
    """
    Class that loggs events to a file

    Attributes
    ----------
    _path: string
        A private string with the log file path
    _fieldnames: list
        A private list with the file's fieldnames
    _mutex: lock object
        A private lock to control file writing

    Methods
    -------
    execute(media : media obj, image: image obj, inf_results: dict)
        Execute the file logging
    """

    _fieldnames = [
        'name',
        'time',
        'label',
        'probability',
        'bbox-x',
        'bbox-y',
        'bbox-width',
        'bbox-height'
    ]

    def __init__(self, name, path):
        """ Constructor for the Log Event object
        """

        self._name = name
        self._path = path
        self._file = None
        self._file = open_file(self._path)
        self._writer = init_writer(self._file, self._fieldnames)
        self._mutex = threading.Lock()

    def __del__(self):
        if self._file:
            self._file.close()

    def _log(self, media, image, inf_results):
        """ Logs the event to the logging file

        Parameters
        ----------
        media : media obj
            The media object
        image : image obj
            The image object
        inf_results : dict
            The inference results
        """

        media_name = media.get_name()
        image_time = image.get_timestamp()

        for instance in inf_results['instances']:
            label_max = find_max_probability(instance['labels'])
            self._writer.writerow({'name': media_name,
                                  'time': image_time,
                                   'label': label_max['label'],
                                   'probability': label_max['probability'],
                                   'bbox-x': instance['bbox']['x'],
                                   'bbox-y': instance['bbox']['y'],
                                   'bbox-width': instance['bbox']['width'],
                                   'bbox-height': instance['bbox']['height']})
        self._file.flush()

    def _is_triggered(self, filters):
        for f in filters:
            if f.is_triggered():
                return True

        return False

    def execute(self, media, image, inf_results, inf_filter):
        """ Executes the log action

        Parameters
        ----------
        media : media obj
            The media object
        image : image obj
            The image object
        inf_results : dict
            The inference results
        """

        if not self._is_triggered(inf_filter):
            return

        self._mutex.acquire()
        self._log(media, image, inf_results)
        self._mutex.release()

    def get_name(self):
        return self._name

    @classmethod
    def make(cls, desc):
        try:
            name = desc["name"]
            location = desc["location"]
        except KeyError as e:
            raise LogEventError("Malformed log event description") from e

        return LogEvent(name, location)
