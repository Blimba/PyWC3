from handle import *
from ..df.commonj import *
import math


class Effect(Handle):
    def __init__(self, x, y, z, path):
        Handle.__init__(self, AddSpecialEffect, path, x, y)
        BlzSetSpecialEffectZ(self._handle, z)
        self.r, self.g, self.b, self.a = 255, 255, 255, 255
        self._x, self._y, self._z = x, y, z

    def destroy(self):
        self.lose()
        DestroyEffect(self._handle)

    # Positioning
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        BlzSetSpecialEffectX(self._handle, x)

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

    def set_position(self, x, y, z):
        self._x, self._y, self._z = x, y, z
        BlzSetSpecialEffectPosition(self._handle, x, y, z)

    @property
    def scale(self):
        return BlzGetSpecialEffectScale(self._handle)

    @scale.setter
    def scale(self, scale):
        BlzSetSpecialEffectScale(self._handle, x)

    def set_matrix_scale(self, x, y, z):
        BlzSetSpecialEffectMatrixScale(self._handle, x, y, z)

    def reset_matrix_scale(self):
        BlzResetSpecialEffectMatrix(self._handle)

    def look_along(self, x, y, z, roll=0):
        xy = math.sqrt(x * x + y * y)
        yaw = math.atan(y, x)
        pitch = math.atan(z, xy)
        BlzSetSpecialEffectOrientation(self._handle, yaw, -pitch, roll)

    def look_at(self, x, y, z, roll=0):
        self.look_along(x - self._x, y - self._y, z - self._z, roll)

    @property
    def color(self):
        return self.r, self.g, self.b, self.a

    @color.setter
    def color(self, v):
        self.r, self.g, self.b, self.a = v  # this probably doesn't work in lua
        self.setColor(self.r, self.g, self.b, self.a)

    def set_color(self, r, g, b, a=-1):
        self.r, self.g, self.b = r, g, b
        BlzSetSpecialEffectColor(self._handle, r, g, b)
        if (a >= 0):
            self.a = a
            BlzSetSpecialEffectAlpha(self._handle, a)

    def animate(self, anim, timescale=1.0):
        if timescale == 1.0:
            BlzPlaySpecialEffect(self._handle, anim)
        else:
            BlzPlaySpecialEffectWithTimeScale(self._handle, anim, timescale)

    def add_sub_animation(self, anim):
        return BlzSpecialEffectAddSubAnimation(self._handle, anim)

    def remove_sub_animation(self, anim):
        return BlzSpecialEffectRemoveSubAnimation(self._handle, anim)

    def clear_sub_animations(self):
        return BlzSpecialEffectClearSubAnimations(self._handle)
