#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import yaml


class YamlFormatError(RuntimeError):
    pass


class YamlFormat:
    """
    Class that parses the app configuration file

    Methods
    -------
    parse(path : str)
        Parses the app configuration file
    """

    def parse(self, path):
        """Parses the app configuration file and return a dictionary with the configuration

        Raises
        ------
        YamlFormatError
            If couldn't find the app configuration file
            If the app configuration file is invalid
        """

        try:
            with open(path, 'r') as stream:
                cfg = yaml.safe_load(stream)
        except FileNotFoundError as e:
            raise YamlFormatError(
                "Unable to find configuration file '%s'" %
                path) from e
        except yaml.parser.ParserError as e:
            raise YamlFormatError(
                "Provided config file '%s' is invalid" %
                path) from e

        return cfg
