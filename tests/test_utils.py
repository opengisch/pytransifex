import unittest
from functools import partial
from time import sleep as tsleep

from pytransifex.utils import concurrently


def fn(a: int, b: int) -> int:
    tsleep(a)
    return a + b


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        it = [1, 2, 3]
        cls.it = it
        cls.args = [tuple([a, b]) for a, b in zip(it, it)]
        cls.partials = [partial(fn, a, b) for a, b in zip(it, it)]
        cls.res = [2, 4, 6]

    def test1_map_async(self):
        res = concurrently(partials=self.partials)
        assert res == self.res

    def test2_map_async(self):
        res = concurrently(fn=fn, args=self.args)
        assert res == self.res


if __name__ == "__main__":
    unittest.main()
