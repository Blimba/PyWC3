from ..std.index import *
from ..std.timer import *
from .cyclist import *
class Periodic(Cyclist):
    period = 0.01
    _first = None

    def __init__(self):
        Cyclist.__init__(self)
        if Periodic._first == None:
            Periodic._first = self
        else:
            Periodic._first.next = self
        self.on_period = None

    def start_periodic(self):
        if Periodic._first == None:
            Periodic._first = self
        else:
            Periodic._first.next = self

    def destroy(self):
        if self == Periodic._first:
            Periodic._first = self.next
        Cyclist.exclude(self)
        if self == Periodic._first:
            Periodic._first = None

    @staticmethod
    def _period():
        node = Periodic._first
        i = 0
        while node != None:
            i += 1
            nnode = node.next
            # try/except blocks leak memory due to anonymous functions, change at some point
            try: node.on_period()
            except: print(Error)
            node = nnode
            if node == Periodic._first or Periodic._first == None: break
        Periodic.num = i
    @staticmethod
    def _init():
        Periodic.timer = Timer(True)
        Periodic.timer.start(Periodic.period, Periodic._period)

AddScriptHook(Periodic._init, MAIN_BEFORE)

class SlowPeriodic(Cyclist):
    period = 0.1
    _first = None

    def __init__(self):
        Cyclist.__init__(self)
        if SlowPeriodic._first == None:
            SlowPeriodic._first = self
        else:
            SlowPeriodic._first.next = self
        self.on_period = None

    def start_periodic(self):
        if SlowPeriodic._first == None:
            SlowPeriodic._first = self
        else:
            SlowPeriodic._first.next = self

    def destroy(self):
        if self == SlowPeriodic._first:
            SlowPeriodic._first = self.next
        Cyclist.exclude(self)
        if self == SlowPeriodic._first:
            SlowPeriodic._first = None

    @staticmethod
    def _period():
        node = SlowPeriodic._first
        i = 0
        while node != None:
            i += 1
            nnode = node.next
            # try/except blocks leak memory due to anonymous functions, change at some point
            try: node.on_period()
            except: print(Error)
            node = nnode
            if node == SlowPeriodic._first or SlowPeriodic._first == None: break
        SlowPeriodic.num = i
    @staticmethod
    def _init():
        SlowPeriodic.timer = Timer(True)
        SlowPeriodic.timer.start(SlowPeriodic.period, SlowPeriodic._period)

AddScriptHook(SlowPeriodic._init, MAIN_BEFORE)