from std.index import *
# from std.timer import Timer
# from std.effect import Effect
from lib.point import *
from lib.vector3 import *
# from df.test import *
from lib.particle import *
# from lib.itimer import *

from std.unit import *

# class Bullet(Particle):
#     def __init__(self,x,y,z):
#         Particle.__init__(
#             self,
#             Effect(x, y, z, r"Abilities\\Weapons\\CannonTowerMissile\\CannonTowerMissile.mdl"),
#             Vector3((math.random()-0.5)*500,(math.random()-0.5)*500,1000*(math.random()+0.5))
#         )
#         self.collision_sampling = 1
#         self.forces.append(G)
#         self.timeout = 3
#     def on_terrainhit(self):
#         self.velocity = self.velocity.reflect(Vector3.terrain_normal(self.position.x,self.position.y))*0.6
#
#     def on_unithit(self,u):
#         self.destroy()
#
# def createParticle(t):
#     p = Bullet(0,0,128)
#     ITimer.start(0.02, createParticle)
class pu(Particle):
    def on_terrainhit(self):
        self.velocity = self.velocity.reflect(Vector3.terrain_normal(self.position.x, self.position.y))
def test():
    u = Unit(0, "hfoo", 0, 0)

    u.weapon(0).damage_tuple = [50,6,2]
    u.name = "unit1"
    u.max_hp = 1000
    u.life = 500
    u.max_mana = 100
    u.mana = 50
    u.ability("Amrf").add().remove()
    abil = u.ability("Adef")
    print(abil.level)
    abil.remove()
    print(u.name)
    u.color(50,100,150)
    u.player_color(5)
    print(u.type)

    p = pu(u,Vector3(-250,-250,1000))
    p.forces.append(G)

    # ITimer.start(1, createParticle)
    # ITimer.start(3, createParticle)


AddScriptHook(test,MAIN_AFTER)
