from .index import *
from .handle import *
from .event import *
from .unit import *

class RegionEvent(ClassEvent):
    enter = 0
    exit = 1
    def __init__(self,regionevent,methodname,getter,*args):
        ClassEvent.__init__(self, methodname, getter, *args)
        self.event_type = regionevent

    def add_region(self,which_region):
        if self.event_type == RegionEvent.enter:
            self.register(TriggerRegisterEnterRegion, which_region)
        else:
            self.register(TriggerRegisterLeaveRegion, which_region)

class Region(Handle):
    _event_enter = None
    _event_leave = None
    def __init__(self, hysteresis=0.0):
        # call handle init twice, so that both regions point to the same instance
        Handle.__init__(self, CreateRegion)
        self.outer = self._handle
        Handle.__init__(self,CreateRegion)
        self.inner = self._handle
        self.units = []
        self.inner_rects = []
        self.outer_rects = []
        self.hysteresis = math.floor(hysteresis / 32) * 32
        Region._event_enter.add_region(self.inner)
        Region._event_leave.add_region(self.outer)

    def __contains__(self, unit):
        return unit in self.units

    def append_rect(self,r):
        minx = math.floor(GetRectMinX(r) / 32) * 32
        maxx = math.floor(GetRectMaxX(r) / 32) * 32
        miny = math.floor(GetRectMinY(r) / 32) * 32
        maxy = math.floor(GetRectMaxY(r) / 32) * 32
        SetRect(r,minx,miny,maxx,maxy)
        self.inner_rects.append(r)
        RegionAddRect(self.inner,r)
        h = self.hysteresis
        r = Rect(minx-h,miny-h,maxx+h,maxy+h)
        self.outer_rects.append(r)
        RegionAddRect(self.outer,r)
        return self

    # set these on new objects
    def on_enter(self, unit):
        return True
    def on_exit(self, unit):
        pass

    def _on_enter_check(self,unit):
        if not unit in self.units:
            if self.on_enter(unit):
                self.units.append(unit)

    def _on_exit_check(self,unit):
        if unit in self.units:
            self.on_exit(unit)
            self.units.remove(unit)

    @staticmethod
    def get_triggering():
        return Handle.get(GetTriggeringRegion())  # can't make a new region from 1, so just return none if we dont have it

    @staticmethod
    def _init():
        Region._event_enter = RegionEvent(RegionEvent.enter, "_on_enter_check", Region.get_triggering, Unit.get_entering)
        Region._event_leave = RegionEvent(RegionEvent.exit, "_on_exit_check", Region.get_triggering, Unit.get_leaving)


AddScriptHook(Region._init, MAIN_BEFORE)