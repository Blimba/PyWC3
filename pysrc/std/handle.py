class Handle:
    handles = {}
    def __init__(self,constructorfunc, *args):
        print("init for ",self)
        self._handle = constructorfunc(*args)
        self.track()

    def track(self):
        print("Tracking",self._handle)
        Handle.handles[self._handle] = self

    def get(handle):
        return Handle.handles[handle]

    def lose(self):
        print("Losing",self._handle)
        del Handle.handles[self._handle]

    def __type__(self):
        return "Handle"