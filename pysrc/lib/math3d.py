import math
from ..df.commonj import *
from ..std.index import *

class Vector3:
    active = []
    reuse = []
    _fifo_buffer_size = 200  # this is the amount of temporary vectors used
    _loc = None
    def __new__(cls):
        if len(Vector3.reuse) > Vector3._fifo_buffer_size:
            o = Vector3.reuse.pop(0)
            Vector3.active.append(o)
            return o
        else:
            o = object.__new__(cls)
            Vector3.active.append(o)
            return o

    def permanent(self):
        Vector3.active.append(self)
        Vector3.reuse.remove(self)
        return self
    def destroy(self):
        Vector3.active.remove(self)
        Vector3.reuse.append(self)


    @staticmethod
    def stats():
        return 'In use: {}, Recycle bin: {}'.format(str(len(Vector3.active)), str(len(Vector3.reuse)))

    def __init__(self,x=0.0,y=0.0,z=0.0,temp=False):
        self.x = x
        self.y = y
        self.z = z
        self.state = 'temporary' if temp else 'active'
        if temp:
            self.destroy()

    def distance(p1,p2):
        dx = p1.x-p2.x
        dy = p1.y-p2.y
        dz = p1.z-p2.z
        return math.sqrt(dx*dx+dy*dy+dz*dz)
    
    def dot(self,v):
        return self.x*v.x+self.y*v.y+self.z*v.z
    def cross(self,v):
        return Vector3(
            self.y*v.z - self.z*v.y,
            self.z*v.x - self.x*v.z,
            self.x*v.y - v.x*self.y,
            True,
        )
    def __gc__(self):
        print('gc for', self)
    # mutable functions
    def add(self,v):
        self.x += v.x
        self.y += v.y
        self.z += v.z
        return self
    def subtract(self,v):
        self.x -= v.x
        self.y -= v.y
        self.z -= v.z
        return self
    def multiply(self,v):
        if isinstance(v, float):
            self.x *= v
            self.y *= v
            self.z *= v
        elif isinstance(v,Vector3):
            self.x *= v.x
            self.y *= v.y
            self.z *= v.z
        return self
    def divide(self,v):
        if isinstance(v, float):
            v = 1/v
            self.x *= v
            self.y *= v
            self.z *= v
        elif isinstance(v,Vector3):
            self.x /= v.x
            self.y /= v.y
            self.z /= v.z
        return self

    # inmutable functions
    def __add__(self, v):
        return Vector3(self.x+v.x, self.y+v.y, self.z+v.z,True)
    def __sub__(self, v):
        return Vector3(self.x-v.x, self.y-v.y, self.z-v.z,True)

    def __mul__(self, other):
        if isinstance(other,float):
            return Vector3(self.x*other, self.y*other, self.z*other,True)
        elif isinstance(other, Vector3):
            return Vector3(self.x*other.x, self.y*other.y, self.z*other.z,True)

    def __truediv__(self, other):
        if isinstance(other,float):
            return Vector3(self.x/other, self.y/other, self.z/other,True)
        elif isinstance(other,Vector3):
            return Vector3(self.x/other.x, self.y/other.y, self.z/other.z,True)

    def __len__(self):
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

    def __str__(self):
        x = str(self.x)
        y = str(self.y)
        z = str(self.z)
        if "." in x: x = x[:x.find(r'.')+2]
        if "." in y: y = y[:y.find(r'.')+2]
        if "." in z: z = z[:z.find(r'.')+2]
        return "Vector3 x: "+x+", y: "+y+", z: "+z

    def normalize(self):
        return self.divide(len(self))

    def get_angle(self,other):
        return self.dot(other)/(len(self) * len(other))

    def project(self,other):
        return other * (self.dot(other)/other.dot(other))

    def rotate(self,axis,theta,direction='cw'):
        if direction != 'cw': theta = -theta
        cos = math.cos(theta)
        return self*cos+axis.cross(self).multiply(math.sin(theta))+axis*self.dot(axis)*(1-cos)

    @staticmethod
    def from_terrain(x,y,temp=False):
        MoveLocation(Vector3._loc,x,y)
        return Vector3(x,y,GetLocationZ(Vector3._loc),temp)
    @staticmethod
    def terrain_normal(x,y,sampling=5):
        x -= sampling / 2
        y -= sampling / 2
        p1 = Vector3.from_terrain(x,y,True)
        p2 = Vector3.from_terrain(x+sampling,y,True)
        p3 = Vector3.from_terrain(x,y+sampling,True)

        v1 = p2-p1
        v2 = p3-p1
        return Vector3.cross(v1,v2).normalize()

    def reflect(self,normal):
        return self - (normal * (self.dot(normal)*2))

    @staticmethod
    def _create_loc():
        Vector3._loc = Location(0,0)
AddScriptHook(Vector3._create_loc, MAIN_BEFORE)

class Line3:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def closest_point(self,p,segment = True):
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        dz = self.p2.z - self.p1.z
        d2 = dx * dx + dy * dy + dz * dz
        nx = ((p.x - self.p1.x) * dx + (p.y - self.p1.y) * dy + (p.z - self.p1.z)) / d2
        if segment:
            if nx < 0: nx = 0
            elif nx > 1: nx = 1
        return Vector3(dx * nx + self.p1.x, dy * nx + self.p1.y, dz * nx + self.p1.z,True)

    def distance(self,p,segment = True):
        lp = self.closest_point(p,segment)
        return lp.distance(p)

    def normal(self,p):
        return self.closest_point(p).subtract(p).normalize()

class Box:
    def __init__(self,minx,miny,minz,maxx,maxy,maxz):
        self.minx = minx
        self.miny = miny
        self.minz = minz
        self.maxx = maxx
        self.maxy = maxy
        self.maxz = maxz
    def __contains__(self, p):
        if isinstance(p, Vector3):
            return p.x >= self.minx and p.x <= self.maxx and p.y >= self.miny and p.y <= self.maxy and p.z >= self.minz and p.z <= self.maxz

    def from_points(self,p1,p2):
        minx = p1.x if p1.x < p2.x else p2.x
        miny = p1.y if p1.y < p2.y else p2.y
        minz = p1.z if p1.z < p2.z else p2.z
        maxx = p1.x if p1.x > p2.x else p2.x
        maxy = p1.y if p1.y > p2.y else p2.y
        maxz = p1.z if p1.z > p2.z else p2.z
        return Box(minx, miny, minz, maxx, maxy, maxz)

    def closest_point(self,p):
        if p in self:
            return Vector3(p.x,p.y,p.z,True)
        if p.z < self.minz:
            if p.x < self.minx:
                if p.y < self.miny:
                    return Vector3(self.minx, self.miny, self.minz,True)
                if p.y > self.maxy:
                    return Vector3(self.minx, self.maxy, self.minz,True)
                return Vector3(self.minx, p.y, self.minz,True)
            if p.x > self.maxx:
                if p.y < self.miny:
                    return Vector3(self.maxx, self.miny, self.minz,True)
                if p.y > self.maxy:
                    return Vector3(self.maxx, self.maxy, self.minz,True)
                return Vector3(self.maxx, p.y, self.minz,True)
            if p.y > self.maxy:
                return Vector3(p.x,self.maxy, self.minz,True)
            if p.y < self.miny:
                return Vector3(p.x, self.miny, self.minz,True)
            return Vector3(p.x, p.y, self.minz,True)
        elif p.z > self.maxz:
            if p.x < self.minx:
                if p.y < self.miny:
                    return Vector3(self.minx, self.miny, self.maxz,True)
                if p.y > self.maxy:
                    return Vector3(self.minx, self.maxy, self.maxz,True)
                return Vector3(self.minx, p.y, self.maxz,True)
            if p.x > self.maxx:
                if p.y < self.miny:
                    return Vector3(self.maxx, self.miny, self.maxz,True)
                if p.y > self.maxy:
                    return Vector3(self.maxx, self.maxy, self.maxz,True)
                return Vector3(self.maxx, p.y, self.maxz,True)
            if p.y > self.maxy:
                return Vector3(p.x,self.maxy, self.maxz,True)
            if p.y < self.miny:
                return Vector3(p.x, self.miny, self.maxz,True)
            return Vector3(p.x, p.y, self.maxz,True)
        if p.x < self.minx:
            if p.y < self.miny:
                return Vector3(self.minx, self.miny, p.z,True)
            if p.y > self.maxy:
                return Vector3(self.minx, self.maxy, p.z,True)
            return Vector3(self.minx, p.y, p.z,True)
        if p.x > self.maxx:
            if p.y < self.miny:
                return Vector3(self.maxx, self.miny, p.z,True)
            if p.y > self.maxy:
                return Vector3(self.maxx, self.maxy, p.z,True)
            return Vector3(self.maxx, p.y, p.z,True)
        if p.y > self.maxy:
            return Vector3(p.x, self.maxy, p.z,True)
        return Vector3(p.x, self.miny, p.z,True)

    def distance(self,p):
        bp = self.closest_point(p)
        return bp.distance(p)

    def normal(self,p):
        n = self.closest_point(p).subtract(p).normalize()
        return n

#     def show(self):
#         Effect(self.minx, self.miny, self.minz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.maxx, self.miny, self.minz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.minx, self.maxy, self.minz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.maxx, self.maxy, self.minz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.minx, self.miny, self.maxz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.maxx, self.miny, self.maxz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.minx, self.maxy, self.maxz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         Effect(self.maxx, self.maxy, self.maxz, r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl")
#         return self
#
# from ..std.effect import *