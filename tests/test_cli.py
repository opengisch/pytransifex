import unittest
from click.testing import CliRunner

from pytransifex.config import Config
from pytransifex.cli import run_cli
from pytransifex.api import Transifex


class TestCli(unittest.TestCase):
    def test_cli(self):
        config = Config("token", "organization", "po")
        _ = Transifex.get(config)
        runner = CliRunner()
        result = runner.invoke(run_cli, ["create_project", "--dry-run", "true"])
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
