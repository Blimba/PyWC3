from .math3d import *
from ..std.effect import *
from ..std.index import *
from .cyclist import *
from ..std.timer import *
from ..std.unit import *
class Force(Vector3):
    def __init__(self,x,y,z):
        self.active = True
        Vector3.__init__(self,x,y,z)
    def __str__(self):
        return "Force x: "+str(self.x)+", y: "+str(self.y)+", z: "+str(self.z)
    def calculate(self,particle):
        return self
    def destroy(self):
        self.active = False

G = Force(0,0,-2000)
def G_func(self,particle):
    a = self * particle.mass
    return a
G.calculate = G_func


class Particle(Cyclist):
    _start = None
    _group = None
    collidables = []
    period = 0.01
    max_size = 128
    def __gc__(self):
        print('freeing',self)

    def __init__(self,obj,velocity=None,mass=1,follow_direction=False,collision_sampling=1,size=10):
        Cyclist.__init__(self)

        if Particle._start == None:
            Particle._start = self
        else:
            Particle._start.next = self
        self.velocity = velocity or Vector3(0, 0, 100)
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
        self.collision_sampling = collision_sampling
        self.size = size
        if size > Particle.max_size:
            Particle.max_size = size
        self.timeout = None
        self.on_unithit = None
        self.on_terrainhit = None
        self.on_timeout = None
        self.height = 0

    def collision_normal(self,pos=None):
        if pos == None: pos = self.position
        if Vector3.from_terrain(pos.x, pos.y, True).z > pos.z:
            return Vector3.terrain_normal(pos.x, pos.y)
        if len(Particle.collidables) > 0:
            for cobj in Particle.collidables:
                if pos in cobj:
                    return cobj.normal(pos)
        return None

    def terrain_point(self,pos=None):
        if pos == None: pos = self.position
        tp = Vector3.from_terrain(pos.x,pos.y, True)
        if len(Particle.collidables) > 0:
            for cobj in Particle.collidables:
                if pos.x > cobj.minx and pos.x < cobj.maxx and pos.y > cobj.miny and pos.y < cobj.maxy:
                    maxz = cobj.maxz
                    if hasattr(cobj,"get_maxz"): maxz = cobj.get_maxz(pos)
                    minz = cobj.minz
                    if hasattr(cobj,"get_minz"): minz = cobj.get_minz(pos)
                    if maxz > tp.z and minz < (pos.z+self.height):
                        tp.z = maxz
        return tp

    def update(self):
        # append forces. Runs through their calculate functions, which can change their behaviour
        for force in self.forces:
            # make sure to remove inactive forces (for garbage collection)
            if not force.active:
                self.forces.remove(force)
                continue
            # apply the force to the velocity based on its calculated force vector on the particle.
            self.velocity.add(force.calculate(self) * (Particle.period / self.mass))
        # do multisample collision
        r = Particle.period / self.collision_sampling
        v = self.velocity * r
        for i in range(self.collision_sampling):
            self.position.add(v)
            # if the object doesn't have a terrainhit function, don't do the collision checking.
            if callable(self.on_terrainhit):
                # get the normal from the function
                normal = self.collision_normal()
                if normal != None:
                    self.position.subtract(v)
                    self.on_terrainhit(normal)
                    if self.dead == False:
                        # certain weird things might cause a nan. Catch it and fix
                        if self.velocity.x != self.velocity.x: self.velocity.x = 0
                        if self.velocity.y != self.velocity.y: self.velocity.y = 0
                        if self.velocity.z != self.velocity.z: self.velocity.z = 0
                        v = self.velocity * r  # could have changed during terrain collision!
                        self.position.add(v)
            if callable(self.on_unithit):
                GroupEnumUnitsInRange(Particle._group, self.position.x, self.position.y, self.size+Particle.max_size, None)
                # change to BlzGroupUnitAt? => yes, it is (sliiiightly) faster!
                u = FirstOfGroup(Particle._group)
                while(u != None):
                    if self.obj != None and self.obj._handle != u:
                        if not IsUnitType(u, UNIT_TYPE_DEAD) and IsUnitInRangeXY(u, self.position.x,self.position.y,self.size):
                            z = BlzGetUnitZ(u)+GetUnitFlyHeight(u)
                            if self.position.z > (z - self.height) and self.position.z < (z+90):  # hardcoded unit height. Replace later!
                                self.position.subtract(v)
                                self.on_unithit(Unit.get(u) or Unit(u))
                                if self.dead == False:
                                    # certain weird things might cause a nan. Catch it and fix
                                    if self.velocity.x != self.velocity.x: self.velocity.x = 0
                                    if self.velocity.y != self.velocity.y: self.velocity.y = 0
                                    if self.velocity.z != self.velocity.z: self.velocity.z = 0
                                    v = self.velocity * r  # could have changed during unit hit!
                                    self.position.add(v)
                    GroupRemoveUnit(Particle._group, u)
                    u = FirstOfGroup(Particle._group)
        # handle timing
        self.time += Particle.period
        if isinstance(self.timeout,float):
            if self.time >= self.timeout:
                if callable(self.on_timeout):
                    self.on_timeout()
                else:
                    self.destroy()
        if self.dead == True:
            return None

    def update_graphics(self):
        if self.obj != None:
            if self.follow_direction == True and callable(self.obj.look_along):
                self.obj.look_along(self.velocity.x, self.velocity.y, self.velocity.z)
            if callable(self.obj.set_position):
                self.obj.set_position(self.position.x, self.position.y, self.position.z)
            else:
                self.obj.x, self.obj.y, self.obj.z = self.position.x, self.position.y, self.position.z

    def destroy(self):
        self.dead = True
        if self.obj != None:
            self.obj.destroy()
            self.obj = None
        if (Particle._start == self):
            Particle._start = self._n
        self.exclude()
        self.position = None
        self.velocity = None
        self._n = None
        self._p = None
        if (Particle._start == self):
            Particle._start = None

    @staticmethod
    def _period():
        node = Particle._start
        while node != None:
            nnode = node.next
            # try/except blocks leak memory due to anonymous functions, change at some point
            try: node.update()
            except: print(Error)
            try: node.update_graphics()
            except: print(Error)
            node = nnode
            if node == Particle._start or Particle._start == None: break
        Timer.get_expired().restart()

    @staticmethod
    def _Start():
        Particle._group = CreateGroup()
        Particle.timer = Timer()
        Particle.timer.start(Particle.period, Particle._period)


AddScriptHook(Particle._Start,MAIN_BEFORE)


