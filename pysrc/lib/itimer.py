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
class ITimer():
    @staticmethod
    def _timeout():
        t = Timer.get_expired()
        try: t._callback(*t._args)
        except: print(Error)
        t.destroy()

    @staticmethod
    def start(time,callback,*args):
        t = Timer()
        t._callback = callback
        t._args = args
        t.start(time,ITimer._timeout)