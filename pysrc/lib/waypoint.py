from ..std.index import *
from .cyclist import *
from ..std.unit import *
from .math2d import *
from ..std.timer import *
class Waypoint(Vector2,Cyclist):
    range = 10
    def __init__(self,x,y,temp=False):
        Vector2.__init__(self,x,y)
        Cyclist.__init__(self)
    def reached(self,obj):
        if abs(obj.x - self.x) < Waypoint.range and abs(obj.y - self.y) < Waypoint.range:
            return True
        return False
class WaypointUnit(Unit,Cyclist):
    period = 0.05
    _start = None
    def __init__(self,playerid,unitid=0,x=0.0,y=0.0,face=0.0,skinid=0):
        Unit.__init__(self,playerid,unitid,x,y,face,skinid)
        Cyclist.__init__(self)
        self.waypoint = None
        if WaypointUnit._start == None:
            WaypointUnit._start = self

    def add_waypoint(self,wp):
        if self.waypoint == None:
            self.waypoint = wp
        else:
            self.waypoint.next = wp
        return self

    def add_waypoints(self,*wps):
        for wp in wps:
            if self.waypoint == None:
                self.waypoint = wp
            else:
                self.waypoint.next = wp
        return self

    def go_to(self,wp=None):
        if wp == None: wp = self.waypoint
        self.order("move",wp.x,wp.y)

    def check(self):
        if self.waypoint != None and (self.waypoint.reached(self) or self.current_order == OrderId("idle")):
            self.waypoint = self.waypoint.next
            self.go_to()

    def destroy(self,hard=False):
        if (WaypointUnit._start == self):
            WaypointUnit._start = self._n
        self.exclude()
        if (WaypointUnit._start == self):
            WaypointUnit._start = None
        Unit.destroy(self,hard)

    @staticmethod
    def _period():
        node = WaypointUnit._start
        while node != None:
            nnode = node.next
            # try/except blocks leak memory due to anonymous functions, change at some point
            try: node.check()
            except: print(Error)
            node = nnode
            if node == WaypointUnit._start or WaypointUnit._start == None: break
        Timer.get_expired().restart()

    @staticmethod
    def _init():
        WaypointUnit._group = CreateGroup()
        WaypointUnit.timer = Timer()
        WaypointUnit.timer.start(WaypointUnit.period, WaypointUnit._period)

AddScriptHook(WaypointUnit._init,MAIN_BEFORE)

