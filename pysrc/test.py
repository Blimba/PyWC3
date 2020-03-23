#ObjEditor=test.json
#RunPy=preprocess.py

from df.commonj import *
from df.test import *
from std.index import *
from lib.click_plane import *
from lib.unitphysics import *
from std.player import *
# from lib.mouseevent import *
#
# class testc:
#     o = None
#     def __new__(cls):
#         if testc.o == None:
#             testc.o = object.__new__()
#         return testc.o
#
# def c():
#     for i in range(100):
#         testc()
#
#
# def test():
#     TimerStart(CreateTimer(),0.01,True,c)



class FloatingPlatform(Box):
    def __init__(self,x,y,z):
        Box.__init__(self, x-64, y-64, z-80, x+64, y+64, z)
        self.clickplane = ClickPlane(x-64, y-64, x+64, y+64, z)
        self.fx = Effect(x,y,z,r"Doodads\\Cinematic\\FootSwitch\\FootSwitch.mdl")
        # self.fx.clear_sub_animations()
        # self.fx.add_sub_animation(SUBANIM_TYPE_ALTERNATE_EX)
        self.fx.animate(ANIM_TYPE_DEATH)

def test():
    offset = [576,0,140]
    mult = [128,128,35]
    lst = [
        Vector3(0, 0, 0),
        Vector3(0, 1, 1),
        Vector3(0, 2, 2),
        Vector3(-1, 2, 3),
        Vector3(-2, 2, 4),
        Vector3(-2, 1, 5),
        Vector3(-2, 0, 6),
        Vector3(-1, 0, 7),
        Vector3(0, 0, 8),
    ]
    for v in lst:
        Particle.collidables.append(FloatingPlatform(v.x*mult[0]+offset[0],v.y*mult[1]+offset[1],v.z*mult[2]+offset[2]))
    for i in range(2):
        pu = PhysicsUnit(0,b'hfoo', 0,0)
        pu.on_death = lambda u: print(u.name + " of red has died.")
    for i in range(2):
        pu = PhysicsUnit(1,'hfoo', 0,-100*i)
        pu.on_death = lambda u: print(u.name + " of blue has died.")
    Player.on_escape = lambda self, p: print(Player.color[GetPlayerId(p)] + GetPlayerName(p) + "|r has pressed escape.")


def test2():
    t = Triangle(
        Vector3(150, 0, 150),
        Vector3(-150, 150, 300),
        Vector3(300, 300, 450)
    ).show()

    for p in [Vector3(150,150,400), Vector3(120,280,600),Vector3(350,150,500)]:
        p.show()
        cp = t.closest_point(p).permanent()
        Line3(p,cp).show()
        z = cp.z
        if t.in_xy(p):
            print('True')
            z = t.xy2z(cp.x,cp.y)
        Vector3(cp.x,cp.y,z).show()



AddScriptHook(test2,MAIN_AFTER)
