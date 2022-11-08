import unittest
from pathlib import Path
from os import remove
from click.testing import CliRunner

from pytransifex.api_new import Transifex
from pytransifex.cli import cli
from pytransifex.config import CliSettings, defaults


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        cls.tx = Transifex(defer_login=True)
        cls.project_slug = "test_project_pytransifex"
        cls.project_name = "Test Project PyTransifex"
        cls.resource_slug = "test_resource_fr"
        cls.resource_name = "Test Resource FR"
        cls.path_to_file = Path(Path.cwd()).joinpath("tests", "test_resource_fr.po")

        if project := cls.tx.get_project(project_slug=cls.project_slug):
            print("Found old project, removing.")
            project.delete()

        print("Creating a brand new project")
        cls.tx.create_project(
            project_name=cls.project_name, project_slug=cls.project_slug, private=True
        )
        """
        cls.runner = CliRunner()

    @classmethod
    def tearDownClass(cls):
        if Path.exists(defaults["config_file"]):
            remove(defaults["config_file"])

    def test1_init(self):
        result = self.runner.invoke(
            cli,
            ["init", "-org", "ORGA", "-p", "PROJECT"],
        )
        passed = result.exit_code == 0
        print(result.output if passed else result)
        assert passed

    def test2_push(self):
        result = self.runner.invoke(cli, ["push", "-in", "SOME_DIRECTORY"])
        passed = result.exit_code == 0 and "No such file" in result.output
        print(result.output if passed else result)
        assert passed

    def test3_pull(self):
        result = self.runner.invoke(cli, ["pull", "-l", "de,fr,it,en"])
        passed = result.exit_code == 0
        print(result.output if passed else result)
        assert passed


if __name__ == "__main__":
    unittest.main()
