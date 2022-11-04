import unittest

from click.testing import CliRunner

from pytransifex.api_old import Transifex
from pytransifex.cli import cli
from pytransifex.config import Config


class TestCli(unittest.TestCase):
    def test_cli(self):
        config = Config("token", "organization", "po")
        _ = Transifex(config)
        runner = CliRunner()
        result = runner.invoke(cli, ["pull", "somedir", "-l", "fr"])
        
        if result.exit_code != 0:
            print(result.output)
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
