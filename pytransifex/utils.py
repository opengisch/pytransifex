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
    with ThreadPoolExecutor() as pool:
        if not partials is None:
            assert args is None and fn is None
            futures = [pool.submit(p) for p in partials]
        elif (not args is None) and (not fn is None):
            assert partials is None
            futures = [pool.submit(fn, *a) for a in args]
        else:
            raise ValueError(
                "Exactly 1 of 'partials' or 'args' must be defined. Found neither was when calling concurrently."
            )
        return [f.result() for f in as_completed(futures)]
