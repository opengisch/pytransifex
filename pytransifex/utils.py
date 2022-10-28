from functools import wraps


def auth_client(f):
    @wraps(f)
    def capture_args(instance, *args, **kwargs):
        if not instance.logged_in:
            instance.login()
        return f(instance, *args, **kwargs)

    return capture_args
