from std.index import *
from df.test import *
from lib.itimer import *
from std.unit import *
from std.region import *

def enter(reg,unit):
    print(unit.name,'has entered with data',unit.data)
    return True

def timeout(t,d):
    print(t,d)
    ITimer.start(1.0, timeout, 5)
def test():
    ITimer.start(1.0,timeout,5)
    u = Unit(0,b'hfoo',0,0)
    u.on_ordered = lambda u: print(u.name,'ordered')
    u.data = 5
    Region().append_rect(Rect(-128,-128,-64,128)).on_enter = enter

AddScriptHook(test, MAIN_AFTER)
