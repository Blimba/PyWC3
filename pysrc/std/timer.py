from handle import *
from ..df.commonj import *

class Timer(Handle):
    def __init__(self,periodic=False):
        self.periodic = periodic
        Handle.__init__(self,CreateTimer)

    def __gc__(self):
        # currently this never runs
        self.destroy()

    def start(self,time,callback):
        self.time = time
        self.callback = callback
        TimerStart(self._handle,time,self.periodic,callback)

    def restart(self):
        if self.callback:
            TimerStart(self._handle,self.time,self.periodic,self.callback)

    @staticmethod
    def get_expired():
        t = Handle.handles[GetExpiredTimer()]
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

    def get_elapsed(self):
        return TimerGetElapsed(self._handle)

    def get_remaining(self):
        return TimerGetRemaining(self._handle)