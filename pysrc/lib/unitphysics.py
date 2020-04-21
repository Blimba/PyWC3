"""

Realistic physical movement of units based on the height of the terrain. Units behave as particles.

"""

from ..std.unit import *
from .particle import *
class Friction(Force):
    def __init__(self,coeff):
        Force.__init__(self,0,0,0)
        self.coeff = coeff
    def calculate(self,particle):
        if particle.is_grounded():
            if particle.collision_object != None:
                if hasattr(particle.collision_object, "velocity"):
                    return (particle.collision_object.velocity - particle.velocity) * (self.coeff)
                return (particle.velocity) * (-self.coeff)
            return (particle.terrain_velocity-particle.velocity) * (self.coeff)
        return self
Friction_Force = Friction(200)
class PhysicsUnit(Unit,Particle):
    # these are the spacer offsets that are used to check unit collisions before they really happen on the unit himself
    # they might need adjustment
    offsets = [
        Vector3(-5, 0, 0),
        Vector3(0, -5, 0),
        Vector3(5, 0, 0),
        Vector3(0, 5, 0),
    ]
    tps = [None,None,None,None]
    def __init__(self,playerid,unitid=0,x=0,y=0,face=0.0,skinid=0):
        Unit.__init__(self,playerid,unitid,x,y,face,skinid)
        Particle.__init__(self,self,Vector3(0,0,0),10,False,0,BlzGetUnitCollisionSize(self._handle))
        UnitAddAbility(self._handle,FourCC('Amrf'))
        UnitRemoveAbility(self._handle,FourCC('Amrf'))
        self.forces.append(G)
        self.height = 90
        self._terrain_flag = False
        self.default_move_speed = self.obj.move_speed
        self.obj.pathing(False)
        self.fall_damage_multiplier = 1
        self.forces.append(Friction_Force)

    def on_walk_terrainhit(self,wv,pv):
        self.position.subtract(wv * (3 / (1 + math.exp((pv.z + 45)/5))))

    def on_terrainhit(self,normal):
        self._onterrain = True
        tp = self.terrain_point()  # terrain point
        pos = self.position+self.velocity  # new position
        pv = pos - tp  # penetration vector
        prv = pv.project(normal)  # project the penetration to the normal
        self.fall_damage(len(prv)-900)
        if self.dead == False:
            self.velocity.subtract(prv)  # impulse normal penetration to velocity
            if len(self.velocity) < 30:
                fc = 0.8 / (1+math.exp((-len(prv)+10)))
                self.velocity.add(self.velocity *  -fc)

    def fall_damage(self,impulse):
        if impulse > 0:
            impulse = 1.05 / (1+math.exp((-impulse+200)/75.))
            self.obj.life = self.obj.life - impulse * self.obj.max_hp * self.fall_damage_multiplier


    def is_grounded(self):
        return self._terrain_flag

    def on_death(self):
        self.destroy()

    def destroy(self,hard=False):
        Particle.destroy(self)
        Unit.destroy(self,hard)

    def on_unithit(self,u):
        z = u.z
        # check if the unit is still in range after moving it back (only happens if the hit isn't caused by velocity but by walking) probably not required?
        if IsUnitInRangeXY(u._handle, self.position.x, self.position.y, self.size) and self.position.z > (z - self.height) and self.position.z < (z + 90):
            if len(self.walking_velocity) > 0.1:
                pv = self.position - Vector3(u.x, u.y, self.position.z,True)
                l = len(pv)
                pv = pv
                v = pv*(1-(self.size + u.collision_size) / l)
                # check if the hitting unit is a physics unit and is walking (self.walking_velocity > 0)
                # if so, remove each unit half the other.
                ws = len(u.walking_velocity) if u.walking_velocity != None else 0.0
                if ws > 0.1:
                    v *= 0.5
                self.position.subtract(v)

    def on_grounded(self):
        self.obj.move_speed = self.default_move_speed

    def on_airborn(self):
        self.obj.move_speed = 0.0
        # fall in the direction he was going
        self.velocity.add(self.walking_velocity * (self.collision_sampling / Particle.period))

    def update(self):
        self._onterrain = False
        self.walking_velocity = Vector3(self.obj.x,self.obj.y,self.position.z,True).subtract(self.position)
        self.position.x = self.obj.x
        self.position.y = self.obj.y
        tp = self.terrain_point()
        # should probably implement the following better...
        if self.collision_object != None and hasattr(self.collision_object, "velocity"):
            self.walking_velocity.subtract(self.collision_object.velocity * (Particle.period / self.collision_sampling))
        if tp.z > self.position.z:
            self._onterrain = True
            self.on_walk_terrainhit(self.walking_velocity,self.position-tp)
            self.position.z = tp.z+0.1
        for i,offset in enumerate(PhysicsUnit.offsets):
            np = self.position+offset
            tp = self.terrain_point(np)
            PhysicsUnit.tps[i] = tp
            if tp.z > np.z:
                self.on_walk_terrainhit(offset*(len(self.walking_velocity)/len(offset)),np - tp)
        self.set_collision_normal(Vector3.cross(PhysicsUnit.tps[2]-PhysicsUnit.tps[0],PhysicsUnit.tps[3]-PhysicsUnit.tps[1]).normalize())
        Particle.update(self)
        if self.dead == False:
            if self._onterrain:
                if not self._terrain_flag:
                    self._terrain_flag = True
                    self.on_grounded()
            else:
                if self._terrain_flag:
                    if abs(self.terrain_point().z-self.position.z) > 25:
                        self._terrain_flag = False
                        self.on_airborn()


