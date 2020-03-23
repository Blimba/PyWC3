"""

Realistic physical movement of units based on the height of the terrain. Units behave as particles.

"""

from ..std.unit import *
from .particle import *

class PhysicsUnit(Unit,Particle):
    # these are the spacer offsets that are used to check unit collisions before they really happen on the unit himself
    # they might need adjustment
    offsets = [
        Vector3(-5, 0, 0),
        Vector3(0, -5, 0),
        Vector3(5, 0, 0),
        Vector3(0, 5, 0),
    ]

    def __init__(self,playerid,unitid,x,y,face=0.0,skinid=0):
        Unit.__init__(self,playerid,unitid,x,y,face,skinid)
        Particle.__init__(self,self,Vector3(0,0,0),10,False,1,BlzGetUnitCollisionSize(self._handle))
        # assert (isinstance(self.obj, Unit))
        UnitAddAbility(self._handle,FourCC('Amrf'))
        UnitRemoveAbility(self._handle,FourCC('Amrf'))
        self.forces.append(G)
        self.height = 90
        self._terrain_flag = False
        self.default_move_speed = self.obj.move_speed
        self.obj.pathing(False)

    def on_walk_terrainhit(self,wv,pv):
        self.position.subtract(wv * (3 / (1 + math.exp((pv.z + 45)/5))))

    def on_terrainhit(self,normal):
        self._onterrain = True
        tp = self.terrain_point()  # terrain point
        pos = self.position+self.velocity  # new position
        pv = pos - tp  # penetration vector
        prv = pv.project(normal)  # project the penetration to the normal
        impulse = len(prv)-900
        if impulse > 0:
            impulse = 1.05 / (1+math.exp((-impulse+200)/75.))
            self.obj.life = self.obj.life - impulse * self.obj.max_hp
        self.velocity.subtract(prv)  # impulse normal penetration to velocity
        friction = self.velocity * -0.8  # apply friction of the terrain to the unit velocity
        self.velocity.add(friction)

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
        if tp.z > self.position.z:
            self._onterrain = True
            self.on_walk_terrainhit(self.walking_velocity,self.position-tp)
            self.position.z = self.terrain_point().z
        for offset in PhysicsUnit.offsets:
            np = self.position+offset
            tp = self.terrain_point(np)
            if tp.z > np.z:
                self.on_walk_terrainhit(offset*(len(self.walking_velocity)/len(offset)),np - tp)
        Particle.update(self)
        if self._onterrain:
            if not self._terrain_flag:
                self._terrain_flag = True
                self.on_grounded()
        else:
            if self._terrain_flag:
                if abs(self.terrain_point().z-self.position.z) > 25:
                    self._terrain_flag = False
                    self.on_airborn()



