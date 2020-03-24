import math
from ..df.commonj import *
from ..std.index import *

class Vector3:
    active = []
    reuse = []
    _fifo_buffer_size = 1000  # this is the amount of temporary vectors used
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

    def copy(self,temp=False):
        return Vector3(self.x,self.y,self.z,temp)

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

    def project_onto_plane(self,normal,origin):
        return self - (normal * normal.dot(self-origin))

    def rotate(self,axis,theta,direction='cw'):
        if direction != 'cw': theta = -theta
        cos = math.cos(theta)
        return self*cos+axis.cross(self).multiply(math.sin(theta))+axis*self.dot(axis)*(1-cos)

    @staticmethod
    def from_terrain(x,y,temp=False):
        MoveLocation(Vector3._loc,x,y)
        return Vector3(x,y,GetLocationZ(Vector3._loc),temp)

    @staticmethod
    def terrain_normal(x,y,sampling=2):
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

    def show(self):
        fx = AddSpecialEffect(r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl",0,0)
        BlzSetSpecialEffectPosition(fx,self.x,self.y,self.z)
        return self

AddScriptHook(Vector3._create_loc, MAIN_BEFORE)

class Line3:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def closest_point(self,p,segment = True):
        v = self.p2-self.p1
        w = p-self.p1
        pv = w.project(v)
        nx = len(pv)
        if segment:
            if nx < 0: return self.p1
            elif nx > len(v): return self.p2
        return self.p1 + pv

    def distance(self,p,segment = True):
        lp = self.closest_point(p,segment)
        return lp.distance(p)

    def normal(self,p):
        return self.closest_point(p).subtract(p).normalize()

    def show(self):
        AddLightningEx("DRAL",False,self.p1.x,self.p1.y,self.p1.z,self.p2.x,self.p2.y,self.p2.z)
        return self

class Triangle:
    def __init__(self,p,q,r):
        self.p = p
        self.q = q
        self.r = r
        self.side_v1 = (q-p).permanent()
        self.side_v2 = (r-p).permanent()
        self.n = Vector3.cross(self.side_v1/100,self.side_v2/100).normalize().permanent()


    def project_point_onto_self(self, v):
        return v-(self.n*(self.n.dot(v-self.p)))

    def __contains__(self, p):
        u = self.side_v1
        v = self.side_v2
        n = self.n
        w = p - self.p
        gamma = u.cross(w).dot(n)  # assuming normalized n
        beta = w.cross(v).dot(n)
        alpha = 1 - gamma - beta
        return (alpha >= 0) and (alpha <= 1) and (beta >= 0) and (beta <= 1) and (gamma >= 0) and (gamma <= 1)

    def closest_point(self,p):
        u = self.side_v1/100
        v = self.side_v2/100
        n = u.cross(v)
        p = self.project_point_onto_self(p)
        w = (p - self.p)/100

        gamma = u.cross(w).dot(n) / n.dot(n)
        beta = w.cross(v).dot(n) / n.dot(n)
        alpha = 1 - gamma - beta
        if (alpha >= 0) and (alpha <= 1) and (beta >= 0) and (beta <= 1) and (gamma >= 0) and (gamma <= 1):
            return p
        if (beta >= 0) and (gamma >= 0) and (beta+gamma) > 1:
            return Line3(self.q,self.r).closest_point(p)
        if (alpha >= 0) and (beta >= 0) and (alpha + beta) > 1:
            return Line3(self.p, self.q).closest_point(p)
        if (alpha >= 0) and (gamma >= 0) and (alpha + gamma) > 1:
            return Line3(self.p, self.r).closest_point(p)
        if alpha > 1:
            return self.p
        if beta > 1:
            return self.q
        return self.r

    def distance(self,p):
        lp = self.closest_point(p)
        return lp.distance(p)

    def normal(self,p):
        return self.closest_point(p).subtract(p).normalize()

    def in_xy(self,p):
        v0 = self.side_v2/10
        v1 = self.side_v1/10
        v2 = (p-self.p)/10
        def dot(v1,v2):
            return v1.x*v2.x+v1.y*v2.y
        dot00 = dot(v0, v0)
        dot11 = dot(v1, v1)
        dot01 = dot(v0, v1)
        dot02 = dot(v0, v2)
        dot12 = dot(v1, v2)
        invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * invDenom
        v = (dot00 * dot12 - dot01 * dot02) * invDenom
        return (u > 0) and (v > 0) and ((u + v) < 1)

    def xy2z(self,x,y):
        dx = x-self.p.x
        dy = y-self.p.y
        dz = (self.n.x*dx+self.n.y*dy)/-self.n.z
        return self.p.z+dz

    def show(self):
        AddLightningEx("DRAL", False, self.p.x, self.p.y, self.p.z, self.q.x, self.q.y, self.q.z)
        AddLightningEx("DRAL", False, self.q.x, self.q.y, self.q.z, self.r.x, self.r.y, self.r.z)
        AddLightningEx("DRAL", False, self.r.x, self.r.y, self.r.z, self.p.x, self.p.y, self.p.z)
        return self

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

    @staticmethod
    def from_points(p1,p2):
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
