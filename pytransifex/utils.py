from pathlib import Path
from typing import Any, Callable, Iterable
from asyncio import run, gather, get_running_loop
from functools import wraps
from inspect import iscoroutinefunction


def ensure_login(f):
    @wraps(f)
    def capture_args(instance, *args, **kwargs):
        if not instance.logged_in:
            instance.login()
        return f(instance, *args, **kwargs)

    return capture_args


def map_async(
    *,
    fn: Callable | None = None,
    args: Iterable[Any] | None = None,
    partials: Iterable[Any] | None = None,
) -> Iterable[Any]:
    async def closure() -> Iterable[Any]:
        tasks = []
        if iscoroutinefunction(fn) and args:
            if partials:
                raise Exception("Partials don't work with coroutine functions!")
            tasks = [fn(*a) for a in args]
        else:
            loop = get_running_loop()
            if partials:
                tasks = [loop.run_in_executor(None, p) for p in partials]
            elif fn and args:
                tasks = [loop.run_in_executor(None, fn, *a) for a in args]
            else:
                raise Exception("Either partials or fn and args!")
        return await gather(*tasks)

    return run(closure())

"""
import aiofiles, aiohttp

async def write_file_async(path: Path, contents: str) -> None:
    async with open(path, "w") as fh:
        await fh.write(contents)


async def get_async_from_url(urls: list[str]) -> list[str]:
    async def get_text(session: ClientSession, url: str) -> str:
        response = await session.get(url)
        return await response.text()

    async with ClientSession() as session:
        return await gather(*[get_text(session, url) for url in urls])
"""