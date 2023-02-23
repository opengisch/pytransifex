import logging
import os
import unittest
from pathlib import Path

import yaml

from tests._translation import Parameters, Translation

logger = logging.getLogger(__name__)


class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test case"""
        transifex_token = os.getenv("TX_TOKEN")
        cls.transifex_token = transifex_token
        assert transifex_token

        config_yaml = Path.cwd().joinpath(
            "tests", "data", ".qgis-plugin-ci-test-changelog.yaml"
        )
        with open(config_yaml) as f:
            arg_dict = yaml.safe_load(f)

        cls.parameters = Parameters(**arg_dict)
        cls.t = Translation(cls.parameters, transifex_token=transifex_token)
        logger.info(f"Set up classed with {cls.parameters}")

    @classmethod
    def tearDownClass(cls):
        assert cls.parameters.project_slug
        cls.t.tx_client.delete_project(cls.parameters.project_slug)

    def test1_creation(self):
        assert self.transifex_token
        self.t = Translation(self.parameters, transifex_token=self.transifex_token)


if __name__ == "__main__":
    unittest.main()
