# from lib.Vector2 import *
from .index import *
# from lib.point import *
from .obj.test import *
# from std.timer import Timer


class A:
    def __gc__(self):
        print(self)
        print('garbage collected')

def test():
    a = A()
    b = A()
    print(_VERSION)
    print(a,b)
    a = None
    b = None
    collectgarbage()


AddScriptHook(test, MAIN_AFTER)


