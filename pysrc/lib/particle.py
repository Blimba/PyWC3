from .math3d import *
from ..std.effect import *
from ..std.index import *
from .periodic import *
from ..std.timer import *
from ..std.unit import *
class Force(Vector3):
    def __init__(self, x, y, z):
        self.active = True
        Vector3.__init__(self, x, y, z)

    def __str__(self):
        return "Force x: "+str(self.x)+", y: "+str(self.y)+", z: "+str(self.z)
    def calculate(self,particle):
        return self
    def destroy(self):
        self.active = False
        Vector3.destroy(self)

G = Force(0,0,-2000)
G.calculate = lambda self, p: self*p.mass

class Spring(Force):
    def __init__(self, x, y, z, strength=1):
        Force.__init__(self,0,0,0)
        self.center = Vector3(x, y, z)
        self.strength = strength
    def calculate(self,particle):
        return (self.center-particle.position)*particle.mass*self.strength

class Particle(Periodic):
    _group = None
    collidables = []
    container = None
    period = Periodic.period  # don't change, might lead to odd effects
    max_size = 128
    _bin = {}
    def __new__(cls,obj,velocity=None,mass=1,follow_direction=False,collision_sampling=0,size=10):
        if cls in Particle._bin and len(Particle._bin[cls]) > 0:
            return Particle._bin[cls].pop()
        else:
            return object.__new__(cls)

    def free(self):
        if type(self) in Particle._bin:
            Particle._bin[type(self)].append(self)
        else:
            Particle._bin[type(self)] = [self]

    def __init__(self,obj,velocity=None,mass=1,follow_direction=False,collision_sampling=0,size=10):
        Periodic.__init__(self)
        self.velocity = velocity or Vector3(0, 0, 0)
        self.follow_direction = follow_direction
        if isinstance(obj,Vector3):
            self.position = obj
            self.obj = None
        else:
            self.obj = obj
            self.position = Vector3(obj.x, obj.y, obj.z)
            self.update_graphics()
        self.time = 0.0
        self.forces = []
        self.mass = mass
        self.dead = False
        self.auto_collision_sampling = False
        if collision_sampling < 1:
            self.auto_collision_sampling = True
        self.collision_sampling = collision_sampling
        self.size = size
        if size > Particle.max_size:
            Particle.max_size = size
        self.timeout = None
        self.on_unithit = None
        self.on_terrainhit = None
        self.on_timeout = None
        self.height = 0

    def destroy(self):
        self.dead = True
        Periodic.destroy(self)
        self.position.destroy()
        self.velocity.destroy()
        self.position = None
        self.velocity = None
        if self.obj != None and self.obj != self:
            self.obj.destroy()
            self.obj = None
        self.free()

    def update_velocity(self,x,y,z):
        self.velocity.x = x
        self.velocity.y = y
        self.velocity.z = z

    def update_position(self,x,y,z):
        self.position.x = x
        self.position.y = y
        self.position.z = z

    def _collided(self, pos=None):
        if pos == None: pos = self.position
        if Vector3.from_terrain(pos.x, pos.y, True).z > pos.z+0.1:
            return True
        if len(Particle.collidables) > 0:
            for cobj in Particle.collidables:
                if pos in cobj:
                    self.collision_object = cobj
                    return True
        return False

    def collision_normal(self,pos=None):
        if pos == None: pos = self.position
        if self.collision_object:
            return self.collision_object.normal(pos)
        return Vector3.terrain_normal(pos.x, pos.y)

    def terrain_point(self,pos=None):
        if pos == None: pos = self.position
        tp = Vector3.from_terrain(pos.x,pos.y, True)
        o = None
        if len(Particle.collidables) > 0:
            for cobj in Particle.collidables:
                if pos.x > cobj.minx and pos.x < cobj.maxx and pos.y > cobj.miny and pos.y < cobj.maxy:
                    maxz = cobj.maxz
                    if callable(cobj.get_maxz):
                        maxz = cobj.get_maxz(pos) or tp.z
                    minz = cobj.minz
                    if callable(cobj.get_minz):
                        minz = cobj.get_minz(pos) or tp.z
                    if maxz > tp.z and minz < (pos.z+self.height):
                        o = cobj
                        tp.z = maxz
        self.collision_object = o
        return tp

    def update(self):

        # append forces. Runs through their calculate functions, which can change their behaviour
        r = (Particle.period / self.mass)
        vel = self.velocity
        for force in self.forces:
            # make sure to remove inactive forces (for garbage collection)
            if not force.active:
                self.forces.remove(force)
                continue
            # apply the force to the velocity based on its calculated force vector on the particle.
            f = force.calculate(self)
            vel.x += f.x * r
            vel.y += f.y * r
            vel.z += f.z * r
        # do multisample collision
        if self.auto_collision_sampling:
            self.collision_sampling = math.floor(len(self.velocity)/(3/Particle.period))+1
        r = Particle.period / self.collision_sampling
        pos = self.position

        for i in range(self.collision_sampling):
            pos.x += vel.x * r
            pos.y += vel.y * r
            pos.z += vel.z * r
            # if the object doesn't have a terrainhit function, don't do the collision checking.
            if callable(self.on_terrainhit):
                # check if the unit is 'in' the terrain or in a collisionobject
                if self._collided():
                    # should probably implement the following better...
                    if self.collision_object != None and hasattr(self.collision_object,"velocity"):
                        cobj_vel = self.collision_object.velocity
                        pos.x += cobj_vel.x * r
                        pos.y += cobj_vel.y * r
                        pos.z += cobj_vel.z * r
                    pos.x -= vel.x * r
                    pos.y -= vel.y * r
                    pos.z -= vel.z * r
                    # get the normal from the function
                    n = self.collision_normal()
                    self.on_terrainhit(n)
                    if self.dead == False:
                        # certain weird things might cause a nan. Catch it and fix
                        self.velocity.fixnan()
                        vel = self.velocity  # could have changed during terrain collision!
                        pos.x += vel.x * r
                        pos.y += vel.y * r
                        pos.z += vel.z * r
                    else:
                        return None

            if callable(self.on_unithit) and self.dead == False:
                GroupEnumUnitsInRange(Particle._group, self.position.x, self.position.y, self.size+Particle.max_size, None)
                # change to BlzGroupUnitAt? => yes, it is (sliiiightly) faster!
                u = FirstOfGroup(Particle._group)
                while(u != None):
                    if self.obj != None and self.obj._handle != u:
                        if not IsUnitType(u, UNIT_TYPE_DEAD) and IsUnitInRangeXY(u, self.position.x,self.position.y,self.size):
                            z = BlzGetUnitZ(u)+GetUnitFlyHeight(u)
                            if self.position.z > (z - self.height) and self.position.z < (z+90):  # hardcoded unit height. Replace later!
                                pos.x -= vel.x * r
                                pos.y -= vel.y * r
                                pos.z -= vel.z * r
                                self.on_unithit(Unit.get(u) or Unit(u))
                                if self.dead == False:
                                    # certain weird things might cause a nan. Catch it and fix
                                    self.velocity.fixnan()
                                    vel = self.velocity  # could have changed during terrain collision!
                                    pos.x += vel.x * r
                                    pos.y += vel.y * r
                                    pos.z += vel.z * r
                                else:
                                    GroupClear(Particle._group)
                                    return None
                    GroupRemoveUnit(Particle._group, u)
                    u = FirstOfGroup(Particle._group)
        if self.dead == True:
            return None
        # container for map bounds safety as well as to prevent units from going where they should not
        if Particle.container and pos not in Particle.container:
            c = Particle.container
            if pos.x < c.minx: pos.x = c.minx
            if pos.y < c.miny: pos.y = c.miny
            if pos.z < c.minz: pos.z = c.minz
            if pos.x > c.maxx: pos.x = c.maxx
            if pos.y > c.maxy: pos.y = c.maxy
            if pos.z > c.maxz: pos.z = c.maxz
        # handle timing
        self.time += Particle.period
        if isinstance(self.timeout,float):
            if self.time >= self.timeout:
                if callable(self.on_timeout):
                    self.on_timeout()
                    self.time = 0.0
                else:
                    self.destroy()


    def update_graphics(self):
        if self.obj != None and self.dead == False:
            if self.follow_direction == True and callable(self.obj.look_along):
                self.obj.look_along(self.velocity.x, self.velocity.y, self.velocity.z)
            if callable(self.obj.set_position):
                self.obj.set_position(self.position.x, self.position.y, self.position.z)
            else:
                self.obj.x = self.position.x
                self.obj.y = self.position.y
                self.obj.z = self.position.z

    def on_period(self):
        if not self.dead:
            self.update()
            self.update_graphics()

    @staticmethod
    def _init():
        Particle._group = CreateGroup()

AddScriptHook(Particle._init,MAIN_BEFORE)