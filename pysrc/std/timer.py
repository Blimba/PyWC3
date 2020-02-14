from handle import *
from ..obj.commonj import *
class Timer(Handle):
    def __init__(self,periodic=False):
        self.periodic = periodic
        Handle.__init__(self,CreateTimer)

    def __gc__(self):
        print("hallo")
        print(self)
        self.destroy()

    def start(self,time,callback):
        self.time = time
        self.callback = callback
        self.track()
        TimerStart(self._handle,time,self.periodic,callback)

    def restart(self):
        if self.callback:
            self.track()
            TimerStart(self._handle,self.time,self.periodic,self.callback)

    @staticmethod
    def getExpired():
        t = Handle.handles[GetExpiredTimer()]
        t.lose()
        return t

    def pause(self):
        PauseTimer(self._handle)
        return self

    def resume(self):
        ResumeTimer(self._handle)
        return self

    def destroy(self):
        self.lose()
        DestroyTimer(self._handle)

    def getElapsed(self):
        return TimerGetElapsed(self._handle)

    def getRemaining(self):
        return TimerGetRemaining(self._handle)