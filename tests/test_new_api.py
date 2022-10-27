import unittest

from pytransifex.config import Config
from pytransifex.api import Transifex
from pytransifex.api_new import TransifexNew
from pytransifex.interfaces import IsTranslator


config = Config("tok", "orga", "ln")


class TestNewApi(unittest.TestCase):
    def test_old_api_satisfies_protocol(self):
        old_api = Transifex(config)
        assert isinstance(old_api, IsTranslator)

    def test_new_api_satisfies_protocol(self):
        new_api = TransifexNew(config)
        assert isinstance(new_api, IsTranslator)


if __name__ == "__main__":
    unittest.main()
