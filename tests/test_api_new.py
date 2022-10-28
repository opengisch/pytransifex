import unittest

from pytransifex.config import Config
from pytransifex.api import Transifex as TOld
from pytransifex.api_new import Transifex as TNew
from pytransifex.interfaces import IsTranslator


config = Config("tok", "orga", "ln")


class TestNewApi(unittest.TestCase):
    def test_old_api_satisfies_protocol(self):
        old_api = TOld(config)
        assert isinstance(old_api, IsTranslator)

    def test_new_api_satisfies_protocol(self):
        new_api = TNew(config, defer_login=True)
        assert isinstance(new_api, IsTranslator)


if __name__ == "__main__":
    unittest.main()
