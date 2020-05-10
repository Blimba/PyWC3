from std.index import *
# from lib.terrainz_grid import *
from df.blizzardj import bj_mapInitialPlayableArea
from lib.unitphysics import PhysicsUnit
from lib.click_plane import ClickPlane
# from std.unit import Unit
# from lib.particle import Spring
# from lib.periodic import Periodic
from std.player import Player
from df.test import *
from lib.mouseevent import MouseEvent
from lib.order_history import *
def chat(p,msg):
    if msg[0] == '!':
        cmd = msg[1:]
        """[[luacode]]
        xpcall(function() load(cmd)() end, function(Error) print(Error) end)
        """


def test():
    Player.on_chat = chat
    PhysicsUnit(0,b'Hamg')
    # ClickPlane(-512,-512,512,512,100)




AddScriptHook(test,MAP_LOAD)

