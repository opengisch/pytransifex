import unittest
from pytransifex.utils import map_async
from functools import partial
from asyncio import sleep as asleep
from time import sleep as tsleep


async def coroutine_fn(a: int, b: int) -> int:
    await asleep(a)
    return a + b


def non_coroutine_fn(a: int, b: int) -> int:
    tsleep(a)
    return a + b


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        it = [1,2,3]
        cls.it = it
        cls.args = [tuple([a, b]) for a, b in zip(it, it)]
        cls.partials = [partial(non_coroutine_fn, a, b) for a, b in zip(it, it)]
        cls.res = [2, 4, 6]

    def test1_map_async(self):
        res = map_async(fn=coroutine_fn, args=self.args)
        assert res == self.res

    def test2_map_async(self):
        res = map_async(partials=self.partials)
        assert res == self.res

    def test_3_map_async(self):
        res = map_async(fn=coroutine_fn, args=self.args)
        assert res == self.res