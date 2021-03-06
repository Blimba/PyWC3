import math
from ..df.commonj import *

class Vector2:
    active = []
    _fifo_buffer_size = 50  # this is the amount of temporary vectors used
    _loc = None

    _bin = {}
    def __new__(cls,x=0.0,y=0.0,temp=False):
        if cls in Vector2._bin and len(Vector2._bin[cls]) > cls._fifo_buffer_size:
            o = Vector2._bin[cls].pop(0)
            cls.active.append(o)
            return o
        else:
            o = object.__new__(cls)
            cls.active.append(o)
            return o

    def permanent(self):
        cls = type(self)
        if self not in cls.active:
            cls.active.append(self)
            Vector2._bin[cls].remove(self)
        return self
    def destroy(self):
        cls = type(self)
        if cls in Vector2._bin:
            if self in Vector2.active:
                cls.active.remove(self)
                Vector2._bin[cls].append(self)
        else:
            cls.active.remove(self)
            Vector2._bin[cls] = [self]

    def __init__(self,x=0.0,y=0.0,temp=False):
        self.x = x
        self.y = y
        if temp:
            self.destroy()
    @staticmethod
    def stats():
        c = 0
        for cls in Vector2._bin:
            c += len(Vector2._bin[cls])
        return 'Vector2 In use: {}, Recycle bin: {}'.format(str(len(Vector2.active)), str(c))
    def distance(p1,p2):
        dx = p1.x-p2.x
        dy = p1.y-p2.y
        return math.sqrt(dx*dx+dy*dy)
    
    def dot(self,v):
        return self.x*v.x+self.y*v.y
    def cross(self,v):
        '''
        Treats the vectors as if they were 3D with z = 0, and returns the z of the cross product.
        :param v:
        :return float:
        '''
        return self.x*v.y - v.x*self.y
    def __add__(self, p):
        return Vector2(self.x + p.x, self.y + p.y,True)
    def __sub__(self, p):
        return Vector2(self.x - p.x, self.y - p.y,True)

    def __mul__(self, other):
        if isinstance(other,float):
            return Vector2(self.x*other, self.y*other,True)
        elif isinstance(other, Vector2):
            return Vector2(self.x*other.x, self.y*other.y,True)

    def __truediv__(self, other):
        if isinstance(other,float):
            return Vector2(self.x/other, self.y/other,True)
        elif isinstance(other,Vector2):
            return Vector2(self.x/other.x, self.y/other.y,True)

    def __len__(self):
        return math.sqrt(self.x*self.x+self.y*self.y)

    def __str__(self):
        return "Vector2 x: "+str(self.x)+", y: "+str(self.y)
    def add(self,v):
        self.x += v.x
        self.y += v.y
        return self
    def subtract(self,v):
        self.x -= v.x
        self.y -= v.y
        return self
    def multiply(self,v):
        if isinstance(v, float):
            self.x *= v
            self.y *= v
        elif isinstance(v,Vector2):
            self.x *= v.x
            self.y *= v.y
        return self
    def divide(self,v):
        if isinstance(v, float):
            v = 1/v
            self.x *= v
            self.y *= v
        elif isinstance(v,Vector2):
            self.x /= v.x
            self.y /= v.y
        return self
    def normalize(self):
        return self.divide(len(self))

    def get_angle(self,other):
        return self.dot(other)/(len(self) * len(other))

    def project(self,other):
        return other * self.dot(other)/other.dot(other)

    def rotate(self,theta,direction='cw'):
        cos = None
        sin = None
        if direction == 'cw':
            cos = math.cos(theta)
            sin = math.sin(theta)
        else:
            cos = math.cos(-theta)
            sin = math.sin(-theta)
        self.x = self.x*cos - self.y*sin
        self.y = self.x*sin + self.y*cos

    def show(self):
        fx = AddSpecialEffect(r"Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl",self.x,self.y)
        return self
class Line2:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def closest_point(self,p,segment = True):
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        d2 = dx * dx + dy * dy
        nx = ((p.x - self.p1.x) * dx + (p.y - self.p1.y) * dy) / d2
        if segment:
            if nx < 0: nx = 0
            elif nx > 1: nx = 1
        return Vector2(dx * nx + self.p1.x, dy * nx + self.p1.y)

    def distance(self,p,segment = True):
        lp = self.closest_point(p,segment)
        return lp.distance(p)

    def normal(self,p):
        return self.closest_point(p).subtract(p).normalize()

    def show(self):
        z1 = GetLocationZ(Location(self.p1.x,self.p1.y))
        z2 = GetLocationZ(Location(self.p2.x, self.p2.y))
        AddLightningEx("DRAL",False,self.p1.x,self.p1.y,z1,self.p2.x,self.p2.y,z2)
        return self

class Rectangle:
    def __init__(self,minx,miny,maxx,maxy):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    @staticmethod
    def from_points(p1,p2):
        minx = p1.x if p1.x < p2.x else p2.x
        miny = p1.y if p1.y < p2.y else p2.y
        maxx = p1.x if p1.x > p2.x else p2.x
        maxy = p1.y if p1.y > p2.y else p2.y
        return Rectangle(minx,miny,maxx,maxy)

    @staticmethod
    def from_rect(rect):
        return Rectangle(GetRectMinX(rect), GetRectMinY(rect), GetRectMaxX(rect), GetRectMaxY(rect))

    def random_point(self,crop=0):
        x = math.random()*(self.maxx-(crop*2)-self.minx)+self.minx+crop
        y = math.random()*(self.maxy-(crop*2)-self.miny)+self.miny+crop
        return Vector2(x,y,True)

    def __contains__(self, p):
        if isinstance(p, Vector2):
            return p.x >= self.minx and p.x <= self.maxx and p.y >= self.miny and p.y <= self.maxy

    def closest_point(self,p):
        if p in self:
            return Vector2(p.x,p.y)
        if p.x < self.minx:
            if p.y < self.miny:
                return Vector2(self.minx, self.miny)
            if p.y > self.maxy:
                return Vector2(self.minx, self.maxy)
            return Vector2(self.minx, p.y)
        if p.x > self.maxx:
            if p.y < self.miny:
                return Vector2(self.maxx, self.miny)
            if p.y > self.maxy:
                return Vector2(self.maxx, self.maxy)
            return Vector2(self.maxx, p.y)
        if p.y > self.maxy:
            return Vector2(p.x,self.maxy)
        return Vector2(p.x,self.miny)

    def distance(self,p):
        rp = self.closest_point(p)
        return rp.distance(p)

    def normal(self,p):
        return self.closest_point(p).subtract(p).normalize()