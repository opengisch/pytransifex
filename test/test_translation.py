#! /usr/bin/env python

import unittest
import os

from pytransifex.api import Transifex

class TestTranslation(unittest.TestCase):

    def setUp(self):
        transifex_token = os.getenv('transifex_token')
        assert transifex_token is not None
        self.t = Transifex(organization='pytransifex', transifex_token=transifex_token)
        self.project_slug = 'PyTransifex'
        self.project_name = 'PyTransifex Test project'
        self.source_lang = 'fr'

    def tearDown(self):
        self.t.delete_projet(self.project_slug)

    def test_creation(self):
        self.t.delete_project()
        self.t.create_project(name=self.project_name,
                              slug=self.project_slug,
                              source_language_code=self.source_lang,
                              private=False,
                              repository_url='https://www.github.com/opengisch/pytransifex')

    def test_pull(self):
        self.t.pull()
        self.t.compile_strings()


if __name__ == '__main__':
    unittest.main()
