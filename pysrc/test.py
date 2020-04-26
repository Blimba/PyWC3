from std.index import *
from lib.terrainz_grid import *
from df.blizzardj import bj_mapInitialPlayableArea
from lib.unitphysics import PhysicsUnit
from std.unit import Unit
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
from HauntedMansion.classes.effecttext import EffectText,Char
def Timeit():
    tlst = []
    for i in range(5):
        t = os.clock()
        for _ in range(1000):
            u.update()
        t = (os.clock()-t)*1000
        tlst.append(t)
        print(t,'ms')
    avgt = 0
    for t in tlst:
        avgt += t
    avgt /= len(tlst)
    std = 0
    for t in tlst:
        std += (t-avgt)**2
    std = math.sqrt(std/len(tlst))
    print('avg: {}, std: {}'.format(avgt,std))
u=None

def footy():
    Unit(0,b'hpea',0,0)
def test():
    Player.on_chat = chat
    u = PhysicsUnit(0,b'hfoo',0,0)
    # Periodic.destroy(u)


    text = EffectText("hello krash", 0, 320, 32, 0.5, 'center').rotate(45).set_pitch(270)
    for c in text[:5]:
        c.set_color(255,200,0)


AddScriptHook(test,MAP_LOAD)

