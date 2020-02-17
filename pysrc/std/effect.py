from handle import *
from ..df.commonj import *
import math

class Effect(Handle):
    def __init__(self,x,y,z,path):
        Handle.__init__(self,AddSpecialEffect,path,x,y)
        BlzSetSpecialEffectZ(self._handle, z)
        self.r, self.g, self.b, self.a = 255,255,255,255
        self._x, self._y, self._z = x,y,z
    def destroy(self):
        self.lose()
        DestroyEffect(self._handle)
    def __type__(self):
        return "PyEffect"
    # Positioning
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,x):
        self._x = x
        BlzSetSpecialEffectX(self._handle,x)
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, y):
        self._y = y
        BlzSetSpecialEffectY(self._handle, y)
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self, z):
        self._z = z
        BlzSetSpecialEffectZ(self._handle, z)
    def setPosition(self,x,y,z):
        self._x, self._y, self._z = x, y, z
        BlzSetSpecialEffectPosition(self._handle,x,y,z)

    @property
    def scale(self):
        return BlzGetSpecialEffectScale(self._handle)
    @scale.setter
    def scale(self,scale):
        BlzSetSpecialEffectScale(self._handle, x)

    def setMatrixScale(self,x,y,z):
        BlzSetSpecialEffectMatrixScale(self._handle,x,y,z)
    def resetMatrixScale(self):
        BlzResetSpecialEffectMatrix(self._handle)

    def lookAlongVector(self,x,y,z,roll=0):
        xy = math.sqrt(x * x + y * y)
        yaw = math.atan(y, x)
        pitch = math.atan(z, xy)
        BlzSetSpecialEffectOrientation(self._handle, yaw, -pitch, roll)
    def lookAt(self,x,y,z,roll=0):
        self.lookAlongVector(x-self._x, y-self._y, z-self._z,roll)

    @property
    def color(self):
        return self.r,self.g,self.b,self.a
    @color.setter
    def color(self,v):
        self.r, self.g, self.b, self.a = *v
        self.setColor(self.r,self.g,self.b,self.a)

    def setColor(self,r,g,b,a=-1):
        self.r, self.g, self.b = r, g, b
        BlzSetSpecialEffectColor(self._handle,r,g,b)
        if(a>=0):
            self.a = a
            BlzSetSpecialEffectAlpha(self._handle,a)

    def animate(self,anim,timescale=1.0):
        if timescale == 1.0:
            BlzPlaySpecialEffect(self._handle,anim)
        else:
            BlzPlaySpecialEffectWithTimeScale(self._handle,anim,timescale)

    def addSubAnimation(self,anim):
        return BlzSpecialEffectAddSubAnimation(self._handle,anim)
    def removeSubAnimation(self,anim):
        return BlzSpecialEffectRemoveSubAnimation(self._handle,anim)
    def clearSubAnimations(self):
        return BlzSpecialEffectClearSubAnimations(self._handle)