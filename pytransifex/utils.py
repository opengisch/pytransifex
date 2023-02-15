from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Callable


def ensure_login(f):
    @wraps(f)
    def capture_args(instance, *args, **kwargs):
        if not instance.logged_in:
            instance.login()
        return f(instance, *args, **kwargs)

    return capture_args


def concurrently(
    *,
    fn: Callable | None = None,
    args: list[Any] | None = None,
    partials: list[Any] | None = None,
) -> list[Any]:
    if args and len(args) == 0:
        return []
    if partials and len(partials) == 0:
        return []

    with ThreadPoolExecutor() as pool:
        if partials:
            futures = [pool.submit(p) for p in partials]
        elif fn and args:
            futures = [pool.submit(fn, *a) for a in args]
        else:
            raise Exception("Either partials or fn and args!")
        return [f.result() for f in as_completed(futures)]
