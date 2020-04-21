from std.index import *
from lib.terrainz_grid import *
from df.blizzardj import bj_mapInitialPlayableArea
from lib.unitphysics import PhysicsUnit
from lib.particle import Spring
from lib.periodic import Periodic
from std.player import Player
from df.test import *
from HauntedMansion.classes.objects import Platform, MovingPlatform
def chat(p,msg):
    if msg[0] == '!':
        cmd = msg[1:]
        """[[luacode]]
        xpcall(function() load(cmd)() end, function(Error) print(Error) end)
        """

# def Timeit():
#     t = os.clock()
#     for _ in range(1000):
#         u.update()
#     print((os.clock()-t)*1000,'ms')

u=None
def test():
    Player.on_chat = chat
    u = PhysicsUnit(0,b'hfoo',0,0)
    u.terrain_velocity.update(100,0,0)
    Platform(512,0,100)
    mp = MovingPlatform(640, 128, 100)
    mp.forces.append(Spring(640,0,100,1))


AddScriptHook(test,MAP_LOAD)

