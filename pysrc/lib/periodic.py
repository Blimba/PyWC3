from ..std.index import *
from ..std.timer import *
from .cyclist import *
class Periodic(Cyclist):
    period = 0.01
    _first = None

    def __init__(self):
        Cyclist.__init__(self)
        self.start_periodic()
        self.on_period = None

    def start_periodic(self):
        if Periodic._first == None:
            Periodic._first = self
        else:
            Periodic._first.next = self

    def stop_periodic(self):
        self.exclude()

    def destroy(self):
        if self == Periodic._first:
            Periodic._first = self.next
        self.exclude()
        if self == Periodic._first:
            Periodic._first = None

    @staticmethod
    def _period():
        node = Periodic._first
        while node != None:
            nnode = node.next
            # try/except blocks leak memory due to anonymous functions, change at some point
            try: node.on_period()
            except: print(Error)
            node = nnode
            if node == Periodic._first or Periodic._first == None: break

    @staticmethod
    def _init():
        Periodic.timer = Timer(True)
        Periodic.timer.start(Periodic.period, Periodic._period)

AddScriptHook(Periodic._init, MAIN_BEFORE)