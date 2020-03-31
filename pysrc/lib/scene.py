from ..std.index import *
from .itimer import *

class Scene:
    def __init__(self,func):
        self.func = func

    def resume(t,self):
        coroutine.resume(self.co,self)

    def pause(self):
        coroutine.pause()

    def wait(self,duration):
        ITimer.start(duration,Scene.resume,self)
        coroutine.pause()

    def start(self):
        self.co = coroutine.create(self.func)
        coroutine.resume(self.co,self)