#! /usr/bin/env python

import unittest
import os

from pytransifex import Transifex, PyTransifexException


class TestTranslation(unittest.TestCase):

    def setUp(self):
        token = os.getenv('TX_TOKEN')
        assert token is not None
        self.t = Transifex(organization='pytransifex', api_token=token)
        self.project_slug = 'pytransifex-test-project'
        self.project_name = 'PyTransifex Test project'
        self.source_lang = 'fr_FR'

    def tearDown(self):
        try:
            self.t.delete_project(self.project_slug)
        except PyTransifexException:
            pass
        try:
            self.t.delete_team('{}-team'.format(self.project_slug))
        except PyTransifexException:
            pass

    def test_creation(self):
        self.tearDown()
        self.t.create_project(
            name=self.project_name,
            slug=self.project_slug,
            source_language_code=self.source_lang,
            private=False,
            repository_url='https://www.github.com/opengisch/pytransifex'
        )

        self.assertTrue(self.t.project_exists(self.project_slug))


if __name__ == '__main__':
    unittest.main()
