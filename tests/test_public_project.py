import unittest
from os import remove
from pathlib import Path

from pytransifex.api import Transifex
from tests import logging, test_config_public

logger = logging.getLogger(__name__)


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        client = Transifex(defer_login=True)
        assert client

        cls.path_to_input_dir = Path.cwd().joinpath("tests", "data", "resources")
        cls.path_to_file = cls.path_to_input_dir.joinpath("test_resource_fr.po")
        cls.output_dir = Path.cwd().joinpath("tests", "output")

        cls.tx = client
        cls.project_slug = test_config_public["project_slug"]
        cls.project_name = test_config_public["project_name"]
        cls.resource_slug = test_config_public["resource_slug"]
        cls.resource_name = test_config_public["resource_name"]
        repository_url = test_config_public["repository_url"]

        if missing := next(
            filter(lambda p: not p.exists(), [cls.path_to_file, cls.path_to_input_dir]),
            None,
        ):
            raise ValueError(
                f"Unable to complete test with broken tests inputs. Found missing: {missing}"
            )

        if project := cls.tx.get_project(project_slug=cls.project_slug):
            logger.info("Found old project, removing.")
            project.delete()

        logger.info("Creating a brand new project")
        cls.tx.create_project(
            project_name=cls.project_name,
            project_slug=cls.project_slug,
            private=False,
            repository_url=repository_url,
        )

    @classmethod
    def tearDownClass(cls):
        if Path.exists(cls.output_dir):
            remove(cls.output_dir)

    def test1_project_exists(self):
        verdict = self.tx.project_exists(project_slug=self.project_slug)
        assert verdict


if __name__ == "__main__":
    unittest.main()
