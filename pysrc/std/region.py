from .index import *
from .handle import *
from .event import *
from .unit import *
"""

    A region class to make working with rects / regions simple
    
    Generating a region:
    
        r = Region()  # optionally, we can supply hysteresis as an argument, see below
        
    Adding rects:
        
        r.append_rect(gg_rct_Region000)  # append a preplaced rect from the editor
        r.append_rect(Rect(-64,-64,64,64))  # or create a new one
        
    For enter and leave events, we simply have to give it a function:
    
        def enter(region,unit):
            if(GetUnitTypeId(unit) == b'hfoo'):
                # only footmen are counted in this region
                return True
            return False

        def leave(region,unit):
            # because we only 'allow' footman in the region, the type of unit is certainly a footman
            print(unit.name,'leaving the region')
        # now, actually put those functions on the region  
        r.on_enter = enter
        r.on_exit = leave
        
    Hysteresis:
    
    Sometimes we want the leave event to not be quite the same as when we entered the rect. That's why we can have an
    additional rect that acts as the 'unit leaves' event instead. It couldn't be simpler to implement:
    
    r = Region(128.0)
    r.append_rect(Rect(-64,-64,64,64))
    r.on_enter = enter
    r.on_exit = leave
    
    now the 'exit' fires 128 outside of the original rect in all directions.

"""
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
        Handle.__init__(self, CreateRegion())
        self.outer = self._handle
        Handle.__init__(self, CreateRegion())
        self.inner = self._handle
        self.units = []
        self.inner_rects = []
        self.outer_rects = []
        self.hysteresis = math.floor(hysteresis / 32) * 32
        self.default_enter = True
        self.active = True
        Region._event_enter.add_region(self.inner)
        Region._event_leave.add_region(self.outer)

    def destroy(self):
        Handle.destroy(self)
        self.active = False

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
        return self.default_enter
    def on_exit(self, unit):
        pass
    def on_first_enter(self,unit):
        pass
    def on_last_exit(self,unit):
        pass

    def _on_enter_check(self,unit):
        if self.active and not unit in self.units:
            if self.on_enter(unit):
                self.units.append(unit)
                if len(self.units) == 1:
                    self.on_first_enter(unit)

    def _on_exit_check(self,unit):
        if self.active and unit in self.units:
            self.on_exit(unit)
            self.units.remove(unit)
            if len(self.units) == 0:
                self.on_last_exit(unit)

    def enter(self,unit):
        if unit not in self.units:
            self.units.append(unit)

    def enter_existing(self):
        for r in self.inner_rects:
            lst = Unit.list_in_rect(r)
            for u in lst:
                self._on_enter_check(u)

    @staticmethod
    def suspend_events():
        Region._event_enter.active = False
        Region._event_leave.active = False

    @staticmethod
    def resume_events():
        Region._event_enter.active = True
        Region._event_leave.active = True

    @staticmethod
    def get_triggering():
        return Handle.get(GetTriggeringRegion())  # can't make a new region from 1, so just return none if we dont have it

    @staticmethod
    def _init():
        Region._event_enter = RegionEvent(RegionEvent.enter, "_on_enter_check", Region.get_triggering, Unit.get_entering)
        Region._event_leave = RegionEvent(RegionEvent.exit, "_on_exit_check", Region.get_triggering, Unit.get_leaving)


AddScriptHook(Region._init, MAIN_AFTER)