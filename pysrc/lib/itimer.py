"""

This small addition to the Timer class makes life a lot easier. Instead of having to track timer handles for simple
tasks, this scripts handles everything automatically, and passes whichever data you give the start function.

For example:

def timeout_function(timervar, data1, data2):
    print(data1,data2)

ITimer.start(3.0, timeout_function, "hello", "from ITimer")

This script would print 'hello  from ITimer' after 3 seconds. Please note how we do not require to destroy the timer
manually.

"""
from ..std.timer import *
from ..std.compatibility import *

# uses ITimer recyclebin
class CTimer():
    @staticmethod
    def _timeout():
        t = Timer.get_expired()
        self = t._instance
        f = t._callback
        try: f(self, *t._args)
        except: print(Error)
        ITimer.recycle.append(t)
    def timer(self,time,callback,*args):
        t = None
        if len(ITimer.recycle) > 5:
            t = ITimer.recycle.pop(0)
        else:
            t = Timer()
        t._instance = self
        t._callback = callback
        t._args = args
        t.start(time, CTimer._timeout)
        return t

class ITimer():
    recycle = []
    @staticmethod
    def _timeout():
        t = Timer.get_expired()
        try: t._callback(*t._args)
        except: print(Error)
        ITimer.recycle.append(t)

    @staticmethod
    def start(time,callback,*args):
        t = None
        if len(ITimer.recycle) > 5:
            t = ITimer.recycle.pop(0)
        else:
            t = Timer()
        t._callback = callback
        t._args = args
        t.start(time,ITimer._timeout)
        return t