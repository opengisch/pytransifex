import logging
import os
import unittest
from pathlib import Path

import yaml

from pytransifex.exceptions import PyTransifexException
from tests._translation import Parameters, Translation

logger = logging.getLogger(__name__)


class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test case"""
        config_yaml = Path.cwd().joinpath(
            "tests", "data", ".qgis-plugin-ci-test-changelog.yaml"
        )
        print(config_yaml)
        with open(config_yaml) as f:
            arg_dict = yaml.safe_load(f)
        transifex_token = os.getenv("TX_TOKEN")
        assert transifex_token
        cls.transifex_token = transifex_token

        cls.parameters = Parameters(**arg_dict)
        cls.t = Translation(cls.parameters, transifex_token=transifex_token)

    def tearDown(self):
        try:
            self.t.tx_client.delete_project(self.parameters.project_slug)
        except PyTransifexException as error:
            logger.debug(error)
        """
        try:
            self.t.tx_client.delete_team(f"{self.parameters.project_slug}-team")
        except PyTransifexException as error:
            logger.debug(error)
        """

    def test1_creation(self):
        self.tearDown()
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)  # type: ignore

    def test2_push(self):
        self.t.update_strings()
        self.t.push()

    def test3_pull(self):
        self.t.pull()
        self.t.compile_strings()


if __name__ == "__main__":
    unittest.main()
