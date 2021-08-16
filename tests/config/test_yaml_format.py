#!/usr/bin/env python3
#  Copyright (C) 2021 RidgeRun, LLC (http://www.ridgerun.com)
#  Authors: Daniel Chaves <daniel.chaves@ridgerun.com>
#           Marisol Zeledon <marisol.zeledon@ridgerun.com>

import unittest

from rr.config.yaml_format import YamlFormat, YamlFormatError


class TestYamlFormat(unittest.TestCase):

    def setUp(self):
        self.formatter = YamlFormat()

    def test_sucess(self):
        yaml = 'tests/config/test_yaml.yaml'
        cfg = self.formatter.parse(yaml)

        self.assertEqual(10, cfg['test'])

    def test_file_not_found(self):
        yaml = 'tests/config/test_yaml_nonexistent.yaml'

        with self.assertRaises(YamlFormatError) as e:
            self.formatter.parse(yaml)

        self.assertEqual(
            "Unable to find configuration file '%s'" %
            yaml, str(
                e.exception))

    def test_invalid(self):
        yaml = 'tests/config/test_yaml_invalid.yaml'

        with self.assertRaises(YamlFormatError) as e:
            self.formatter.parse(yaml)

        self.assertEqual(
            "Provided config file '%s' is invalid" %
            yaml, str(
                e.exception))


if __name__ == '__main__':
    unittest.main()
