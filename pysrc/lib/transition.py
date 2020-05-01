# from ..std.index import *

from .periodic import *


class _EASE_LINEAR:
    _bin = {}
    def __new__(cls, *args):
        if cls in _EASE_LINEAR._bin and len(_EASE_LINEAR._bin[cls]) > 10:
            return _EASE_LINEAR._bin[cls].pop(0)
        else:
            return object.__new__(cls)

    def destroy(self):
        if type(self) in _EASE_LINEAR._bin:
            if self not in _EASE_LINEAR._bin[type(self)]:
                _EASE_LINEAR._bin[type(self)].append(self)
        else:
            _EASE_LINEAR._bin[type(self)] = [self]

    def __init__(self, duration, start, stop):
        self.t_tot = duration
        self.start = start
        self.stop = stop
        self.d = self.stop - self.start
        self.status = 1

    def calculate_velocity(self, t):
        return self.d / t

    def calculate(self, t):
        return self.start + self.d * t

    def step(self, t):
        if t > self.t_tot:
            t = self.t_tot
            self.status = 0
        return self.calculate(t)


class _EASE_LINEAR_RAD(_EASE_LINEAR):
    def __init__(self, duration, start, stop):
        _EASE_LINEAR.__init__(self,duration,start,stop)
        while self.d < 0: self.d += 360.0
        while self.d > 360: self.d -= 360
        if abs(self.d) < (self.d - 360):
            self.d -= 360
        self.status = 1

class _EASE_CON_A(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        self.a = 2 * (self.d - v0 * duration) / (duration * duration)

    def calculate_velocity(self, t):
        return self.v0 + self.a * t

    def calculate(self, t):
        return self.start + self.v0 * t + 0.5 * self.a * t * t

class _EASE_CON_A_RAD(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        while self.d < 0: self.d += 360.0
        while self.d > 360: self.d -= 360
        if abs(self.d - v0 * duration) < abs((self.d - 360) - v0 * duration):
            self.a = 2 * (self.d - v0 * duration) / (duration * duration)
        else:
            self.a = 2 * ((self.d - 360) - v0 * duration) / (duration * duration)

    def calculate_velocity(self, t):
        return self.v0 + self.a * t

    def calculate(self, t):
        return self.start + self.v0 * t + 0.5 * self.a * t * t


class _EASE_SPL_A(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0=0.0, v_end=0.0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        self.v_end = v_end
        self.t_2 = duration / 2
        self.a2 = (0.5 * v0 + 1.5 * v_end) / self.t_2 - self.d / (self.t_2 * self.t_2)
        self.a1 = (v_end - v0) / self.t_2 - self.a2

    def calculate_velocity(self, t):
        t1 = t if t < self.t_2 else self.t_2
        t2 = 0 if t < self.t_2 else t - self.t_2
        return (self.v0 + self.a1 * t1 + self.a1 * self.t_2 + self.a2 * t2)

    def calculate(self, t):
        t1 = t if t < self.t_2 else self.t_2
        t2 = 0 if t < self.t_2 else t - self.t_2
        return self.start + (self.v0 * t + 0.5 * self.a1 * t1 * t1 + self.a1 * t2 * t1 + 0.5 * self.a2 * t2 * t2)

class _EASE_SPL_A_RAD(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0=0.0, v_end=0.0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        self.v_end = v_end
        self.t_2 = duration / 2
        while self.d < 0: self.d += 360.0
        while self.d > 360: self.d -= 360
        if abs(self.d - v0 * duration) < abs((self.d - 360) - v0 * duration):  # fix this!
            self.a2 = (0.5 * v0 + 1.5 * v_end) / self.t_2 - self.d / (self.t_2 * self.t_2)
            self.a1 = (v_end - v0) / self.t_2 - self.a2
        else:
            self.a2 = (0.5 * v0 + 1.5 * v_end) / self.t_2 - (self.d-360) / (self.t_2 * self.t_2)
            self.a1 = (v_end - v0) / self.t_2 - self.a2

    def calculate_velocity(self, t):
        t1 = t if t < self.t_2 else self.t_2
        t2 = 0 if t < self.t_2 else t - self.t_2
        return (self.v0 + self.a1 * t1 + self.a1 * self.t_2 + self.a2 * t2)

    def calculate(self, t):
        t1 = t if t < self.t_2 else self.t_2
        t2 = 0 if t < self.t_2 else t - self.t_2
        return self.start + (self.v0 * t + 0.5 * self.a1 * t1 * t1 + self.a1 * t2 * t1 + 0.5 * self.a2 * t2 * t2)

class _EASE_SM_A(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0=0.0, v_end=0.0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        self.v_end = v_end
        dsq = (duration * duration)
        self.a = 6 * self.d / dsq - (2 * v_end + 4 * v0) / duration
        self.A = 3 * (v0 + v_end) / dsq - 6 * self.d / (duration * dsq)

    def calculate_velocity(self, t):
        return self.v0 + self.a * t + self.A * t * t

    def calculate(self, t):
        return self.start + self.v0 * t + 0.5 * self.a * t * t + self.A * t * t * t / 3

class _EASE_SM_A_RAD(_EASE_LINEAR):
    def __init__(self, duration, start, stop, v0=0.0, v_end=0.0):
        _EASE_LINEAR.__init__(self, duration, start, stop)
        self.v0 = v0
        self.v_end = v_end
        dsq = (duration * duration)
        while self.d < 0: self.d += 360.0
        while self.d > 360: self.d -= 360
        if abs(3 * (v0 + v_end) / dsq - 6 * self.d / (dsq*duration)) < abs(3 * (v0 + v_end) / dsq - 6 * (self.d-360) / (dsq*duration)):
            self.a = 6 * self.d / dsq - (2 * v_end + 4 * v0) / duration
            self.A = 3 * (v0 + v_end) / dsq - 6 * self.d / (duration * dsq)
        else:
            self.a = 6 * (self.d - 360) / dsq - (2 * v_end + 4 * v0) / duration
            self.A = 3 * (v0 + v_end) / dsq - 6 * (self.d - 360) / (duration * dsq)

    def calculate_velocity(self, t):
        return self.v0 + self.a * t + self.A * t * t

    def calculate(self, t):
        return self.start + self.v0 * t + 0.5 * self.a * t * t + self.A * t * t * t / 3

class Transition(Periodic):
    @staticmethod
    def Smooth_Acceleration_Angular(duration, start, stop, v0=0.0, v_end=0.0):
        return _EASE_SM_A_RAD(duration, start, stop, v0, v_end)
    @staticmethod
    def Smooth_Acceleration(duration,start,stop,v0=0.0,v_end=0.0):
        return _EASE_SM_A(duration,start,stop,v0,v_end)

    @staticmethod
    def Split_Acceleration_Angular(duration, start, stop, v0=0.0, v_end=0.0):
        return _EASE_SPL_A_RAD(duration, start, stop, v0, v_end)
    @staticmethod
    def Split_Acceleration(duration, start, stop, v0=0.0, v_end=0.0):
        return _EASE_SPL_A(duration, start, stop, v0, v_end)

    @staticmethod
    def Constant_Acceleration_Angular(duration, start, stop, v0=0.0):
        return _EASE_CON_A_RAD(duration, start, stop, v0)
    @staticmethod
    def Constant_Acceleration(duration, start, stop, v0=0.0):
        return _EASE_CON_A(duration, start, stop, v0)

    @staticmethod
    def Linear_Angular(duration, start, stop):
        return _EASE_SM_A_RAD(duration, start, stop)
    @staticmethod
    def Linear(duration, start, stop):
        return _EASE_SM_A(duration, start, stop)

    _methods = [_EASE_LINEAR,_EASE_LINEAR_RAD,_EASE_CON_A,_EASE_CON_A_RAD,_EASE_SPL_A,_EASE_SPL_A_RAD,_EASE_SM_A,_EASE_SM_A_RAD]
    @staticmethod
    def Method(method,duration,start,stop,v0=0.0,v_end=0.0):
        if method=='linear':
            return _EASE_LINEAR(duration,start,stop)
        elif method=='constant':
            return _EASE_CON_A(duration,start,stop,v0)
        elif method=='split':
            return _EASE_SPL_A(duration,start,stop,v0,v_end)
        elif method=='smooth':
            return _EASE_SM_A(duration,start,stop,v0,v_end)
    @staticmethod
    def MethodRad(method,duration,start,stop,v0=0.0,v_end=0.0):
        if method=='linear':
            return _EASE_LINEAR_RAD(duration,start,stop)
        elif method=='constant':
            return _EASE_CON_A_RAD(duration,start,stop,v0)
        elif method=='split':
            return _EASE_SPL_A_RAD(duration,start,stop,v0,v_end)
        elif method=='smooth':
            return _EASE_SM_A_RAD(duration,start,stop,v0,v_end)

    _bin = {}
    def __new__(cls, *args):
        if cls in Transition._bin and len(Transition._bin[cls]) > 10:
            return Transition._bin[cls].pop(0)
        else:
            return object.__new__(cls)

    def __init__(self,func,*args):
        Periodic.__init__(self)
        self.func = func
        self.args = args
        self.t = 0
        self._lst = [arg for arg in args]
        self.active = True
        self.dwd = False

    def destroy(self):
        if self.active:
            Periodic.destroy(self)
        for i,arg in enumerate(self.args):
            if type(arg) in Transition._methods:
                arg.destroy()
        if type(self) in Transition._bin:
            if self not in Transition._bin[type(self)]:
                Transition._bin[type(self)].append(self)
        else:
            Transition._bin[type(self)] = [self]

    def destroy_when_done(self):
        self.dwd = True
        return self

    def on_period(self):
        cont = False
        self.t += Periodic.period
        for i,arg in enumerate(self.args):
            if type(arg) in Transition._methods:
                self._lst[i] = arg.step(self.t)
                if arg.status == 1:
                    cont = True

        f = self.func
        f(*self._lst)
        if not cont:
            self.t -= Periodic.period
            self.active = False
            Periodic.destroy(self)
            if self.dwd:
                self.destroy()

