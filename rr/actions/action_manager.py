#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

from rr.actions.log_event import LogEvent
from rr.actions.record_event import RecordEvent


class FilterError(RuntimeError):
    pass


class Filter:
    def __init__(self, name, labels, probability):
        self._name = name
        self._labels = labels
        self._probability = probability
        self._is_triggered = False

    def apply(self, prediction):
        self._is_triggered = False

        for instance in prediction["instances"]:
            for label in instance["labels"]:
                if label["class"] in self._labels and label["probability"] >= self._probability:
                    self._is_triggered = True
                    return

    def is_triggered(self):
        return self._is_triggered

    @classmethod
    def make(cls, desc):
        try:
            name = desc["name"]
            labels = desc["labels"] if isinstance(
                desc["labels"], list) else [desc["labels"]]
            probability = desc["threshold"]
        except KeyError as e:
            raise FilterError("Malformed filter description") from e

        return Filter(name, labels, probability)


class ActionError(RuntimeError):
    pass


class Action:
    @classmethod
    def make(cls, desc):
        try:
            atype = desc["type"]
        except KeyError as e:
            raise ActionError("No type specified for action") from e

        if atype == "log_event":
            return LogEvent.make(desc)
        elif atype == "record_event":
            return RecordEvent.make(desc)
        else:
            raise ActionError('Unkown action "%s"' % atype)


class TriggerError(RuntimeError):
    pass


class Trigger:
    def __init__(self, name, action, filters):
        self._name = name
        self._action = action
        self._filters = filters

    def execute(self, prediction, image, media):
        for filter in self._filters:
            filter.apply(prediction)

        self._action.execute(media, image, prediction, self._filters)

    @classmethod
    def make(cls, desc, all_actions, all_filters):
        try:
            name = desc["name"]
            req_action = desc["action"]
            req_filters = desc["filters"]
        except KeyError as e:
            raise TriggerError("Malformed trigger description") from e

        action = None
        for candidate in all_actions:
            if candidate.get_name() == req_action:
                action = candidate
                break

        if not action:
            raise TriggerError('Unknown action "%s"' % req_action)

        filters = []
        for req in req_filters:
            match = None
            for candidate in all_filters:
                if req == candidate.get_name():
                    match = candidate
                    break

            if match is not None:
                filters.append(match)
            else:
                raise TriggerError('Unknown filter "%s"' % req)

        return Trigger(name, action, filters)


class ActionManager:
    def __init__(self, triggers):
        self._triggers = triggers

    def execute(self, prediction, image, media):
        if self._triggers is None:
            return

        for trigger in self._triggers:
            trigger.execute(prediction, image, media)
