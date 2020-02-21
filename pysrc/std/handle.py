class Handle:
    handles = {}

    def __init__(self, constructorfunc, *args):
        self._handle = constructorfunc(*args)
        self.track()

    def track(self):
        Handle.handles[self._handle] = self

    @staticmethod
    def get(handle):
        return Handle.handles[handle]

    def lose(self):
        del Handle.handles[self._handle]

    @property
    def handle(self):
        return self._handle
