class Handle:
    handles = {}

    def __init__(self, constructorfunc, *args):
        # constructorfunc can be a function that returns a handle, or a handle directly
        if callable(constructorfunc):
            self._handle = constructorfunc(*args)
        else:
            self._handle = constructorfunc
            if self.get(constructorfunc) != None:
                print("Warning: secondary object created for handle ", constructorfunc)
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
