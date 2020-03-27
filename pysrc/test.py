from std.index import *
from df.test import *
from lib.waypoint import *
            
def test():
    print("hello world")
    wpu = WaypointUnit(0,b'hfoo')
    wpu.add_waypoints(
        Waypoint(128, 0),
        Waypoint(0, 128),
        Waypoint(-128, 0),
        Waypoint(0, -128),
    )

    
    
AddScriptHook(test, MAIN_AFTER)
