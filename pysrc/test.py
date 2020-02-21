from std.index import *
from std.timer import Timer
from std.effect import Effect
from lib.point import *
from lib.vector3 import *
from df.test import *
from lib.particle import *
fx = None
def rotate():
    p = Point3.from_terrain(GetUnitX(gg_unit_hpea_0000),GetUnitY(gg_unit_hpea_0000))
    v = Vector3.terrain_normal(p.x,p.y)
    # fx.look_at(p.x,p.y,p.z)
    fx.look_along(v.x,v.y,v.z)
    Timer.get_expired().restart()

def destroyParticle():
    t = Timer.get_expired()
    print(t.data,type(t.data))
    t.data.destroy()

def createParticle():
    print("creating")
    p = Particle(0,0,0,0,0,0)
    t = Timer()
    t.start(2.0,destroyParticle)
    t.data = p

def test():
    fx = Effect(0,0,128,r"Abilities\\Weapons\\CannonTowerMissile\\CannonTowerMissile.mdl")

    t = Timer()
    t.start(0.01,rotate)

    Timer().start(2, createParticle)
    Timer().start(3, createParticle)


AddScriptHook(test,MAIN_AFTER)
