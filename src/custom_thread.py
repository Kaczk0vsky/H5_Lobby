from threading import Thread


class CustomThread(Thread):
    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs={},
        verbose=None,
        deamon=None,
    ):
        super().__init__(group, target, name, args, kwargs, daemon=deamon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return
