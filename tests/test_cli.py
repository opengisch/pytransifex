import unittest
from os import remove
from pathlib import Path

from click.testing import CliRunner

from pytransifex.api import Transifex
from pytransifex.cli import cli
from tests import logging, test_config

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
        cls.project_slug = test_config["project_slug"]
        cls.project_name = test_config["project_name"]
        cls.resource_slug = test_config["resource_slug"]
        cls.resource_name = test_config["resource_name"]

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
            project_name=cls.project_name, project_slug=cls.project_slug, private=True
        )

        cls.runner = CliRunner()

    @classmethod
    def tearDownClass(cls):
        if Path.exists(cls.output_dir):
            remove(cls.output_dir)

    def test1_init(self):
        result = self.runner.invoke(
            cli,
            ["init", "-p", self.project_slug, "-org", "test_pytransifex"],
        )
        passed = result.exit_code == 0
        assert passed

    def test2_push(self):
        result = self.runner.invoke(cli, ["push", "-in", str(self.path_to_input_dir)])
        passed = result.exit_code == 0
        logger.info(result.output)
        assert passed

    def test3_pull(self):
        result = self.runner.invoke(cli, ["pull", "-l", "fr_CH,en_GB"])
        passed = result.exit_code == 0
        logger.info(result.output)
        assert passed


if __name__ == "__main__":
    unittest.main()
