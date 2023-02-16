import unittest
from os import remove
from pathlib import Path

from click.testing import CliRunner

from pytransifex.api import Transifex
from pytransifex.cli import cli


class TestCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tx = Transifex(defer_login=True)
        cls.project_slug = "test_project_pytransifex"
        cls.project_name = "Test Project PyTransifex"
        cls.resource_slug = "test_resource_fr"
        cls.resource_name = "Test Resource FR"
        cls.path_to_input_dir = Path.cwd().joinpath("tests", "input")
        cls.path_to_file = cls.path_to_input_dir.joinpath("test_resource_fr.po")
        cls.output_dir = Path.cwd().joinpath("tests", "output")

        if missing := next(
            filter(lambda p: not p.exists(), [cls.path_to_file, cls.path_to_input_dir]),
            None,
        ):
            raise ValueError(
                f"Unable to complete test with broken tests inputs. Found missing: {missing}"
            )

        if project := cls.tx.get_project(project_slug=cls.project_slug):
            print("Found old project, removing.")
            project.delete()

        print("Creating a brand new project")
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
        print(result.output)
        assert passed

    def test3_pull(self):
        result = self.runner.invoke(cli, ["pull", "-l", "fr_CH,en_GB"])
        passed = result.exit_code == 0
        print(result.output)
        assert passed


if __name__ == "__main__":
    unittest.main()
