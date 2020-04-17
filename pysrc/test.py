from std.index import *
# # from df.test import *
# from std.player import *
# from lib.particle import *
# from lib.itimer import ITimer
# from std.effect import Effect
# def chat(p,msg):
#     if msg[:5] == "-lua ":
#         cmd = msg[5:]
#         """[[luacode]]
#         xpcall(function() load(cmd)() end, function(Error) print(Error) end)
#         """

# class p(Particle):
#     def __init__(self):
#         Particle.__init__(
#             self,
#             Effect(0,0,0,r"Abilities\\Weapons\\AncientProtectorMissile\\AncientProtectorMissile.mdl"),
#             Vector3(math.random()*256-128,math.random()*256-128,1500)
#         )
#         self.forces.append(G)
#         self.timeout = 2.0
#     def on_terrainhit(self,normal):
#         self.velocity.update_vector(self.velocity.reflect(normal))
# def timeout():
#     p()
#     # print(Vector3.stats(Vector3),Periodic.num)
#     ITimer.start(0.015,timeout)
# from lib.camera import *
# from lib.click_plane import *
# from std.unit import Unit
# from lib.scene import *

def test():
    print('ha1')
    # RunPy=preproc.py
    # RunPy=preproc.py
    # RunPy=preproc.py
    print('ha2')

AddScriptHook(test, MAP_LOAD)



