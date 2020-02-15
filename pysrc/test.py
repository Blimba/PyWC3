from std.index import *
from std.timer import Timer
def timeout():
    t = Timer.getExpired()
    print(t.data,type(t))
    t.destroy()
def test():
    t = Timer()
    t.data = 5
    t.start(1.0,timeout)

AddScriptHook(test,MAIN_AFTER)
