import functools

from utils.custom_thread import CustomThread


def run_in_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = CustomThread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper
