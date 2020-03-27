from handle import *
from ..df.commonj import *
"""

    A wrapper for the blizzard timers
    
    Usage:
    
    def timeout():
        t = Timer.get_expired()
        print(t.data)
        t.destroy()
    t = Timer()
    # do whatever you want with, such as attach things that we can use on timeout
    t.data = 5
    t.start(1.0, timeout)

"""
class Timer(Handle):
    def __init__(self,periodic=False):
        self.periodic = periodic
        Handle.__init__(self,CreateTimer)

    def __gc__(self):
        # currently this never runs
        print('timer gc',self._handle,self.get_elapsed())
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
        return Handle.get(GetExpiredTimer())

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