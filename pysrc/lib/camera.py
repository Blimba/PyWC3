from ..df.blizzardj import bj_MAX_PLAYERS
from ..df.commonj import *
from .math3d import Vector3
from ..std.index import *
from .transition import *
import math
from ..lib.itimer import CTimer
from ..lib.sync import NumberSync
class Camera(Periodic):
    norm_fields = [CAMERA_FIELD_TARGET_DISTANCE, CAMERA_FIELD_FARZ]
    ang_fields = [CAMERA_FIELD_ANGLE_OF_ATTACK, CAMERA_FIELD_ROTATION,CAMERA_FIELD_FIELD_OF_VIEW]
    _players = {}
    @staticmethod
    def from_player(i):
        if i in Camera._players:
            return Camera._players[i]
        return Camera(i)
    def __init__(self,players=None):
        if players == None:
            players = [i for i in range(bj_MAX_PLAYERS)]
        Periodic.__init__(self)
        if isinstance(players,list):
            self.players = players
        else:
            self.players = [players]
        self.transitions = {}
        self.velocities = {}
        for player in self.players:
            if player in Camera._players:
                Camera._players[player].destroy()
            Camera._players[player] = self
        self.lock_z = True
        self.shake_amount = 0.0
        self.shake_dim = 0.0

    @staticmethod
    def sync_eye_position(playerid, callback, *args):
        def _sync(ns):
            callback(ns,*args)
        NumberSync(Player(playerid),_sync, GetCameraEyePositionX(), GetCameraEyePositionY(), GetCameraEyePositionZ())

    def destroy(self):
        for key in self.transitions:
            self.transitions[key].destroy()
            del self.transitions[key]
            del self.velocities[key]
        Periodic.destroy(self)

    def on_period(self):
        z = 0
        if self.shake_amount > 0:
            z += (math.random() - 0.5) * self.shake_amount
            self.shake_amount *= self.shake_dim
            if self.shake_amount < 10: self.shake_amount = 0
        if GetPlayerId(GetLocalPlayer()) in self._players and self.lock_z:
            if 'z' not in self.transitions or not self.transitions['z'].active:
                z += GetCameraField(CAMERA_FIELD_ZOFFSET) - GetCameraTargetPositionZ()
                SetCameraField(CAMERA_FIELD_ZOFFSET, z, - 0.01)
                SetCameraField(CAMERA_FIELD_ZOFFSET, z, 0.01)

    def shake(self,amount,dim = 0.9):
        self.shake_amount = amount
        self.shake_dim = dim

    def pan_z_instant(self,z):
        if self.shake_amount > 0:
            z += (math.random() - 0.5) * self.shake_amount
            self.shake_amount *= self.shake_dim
            if self.shake_amount < 10: self.shake_amount = 0
        if GetPlayerId(GetLocalPlayer()) in self._players:
            SetCameraField(CAMERA_FIELD_ZOFFSET, z, - 0.01)
            SetCameraField(CAMERA_FIELD_ZOFFSET, z, 0.01)
    def pan_to_instant(self,x,y):
        if GetPlayerId(GetLocalPlayer()) in self._players:
            PanCameraToTimed(x,y,Periodic.period)
    def pan_field_instant(self,field,value):
        if GetPlayerId(GetLocalPlayer()) in self._players:
            SetCameraField(field,value,Periodic.period)
    def pan_z(self,value,duration,method='smooth'):
        if method == 'instant' or duration <= Periodic.period:
            self.transitions['z'].destroy()
            self.pan_z_instant(value)
            return self
        if 'z' in self.transitions:
            self.velocities['z'] = self.transitions['z'].args[1].calculate_velocity(self.transitions['z'].t)
            self.transitions['z'].destroy()
        else:
            self.velocities['z'] = 0.0
        self.transitions['z'] = Transition(
            self.pan_z_instant,self,
            Transition.Method(method,duration,GetCameraField(CAMERA_FIELD_ZOFFSET),value, self.velocities['z'], 0.0),
        )
        return self
    def pan_field(self,field,value,duration,method='smooth'):
        if method == 'instant' or duration <= Periodic.period:
            self.transitions[field].destroy()
            self.pan_field_instant(field,value)
            return self
        if field in self.transitions:
            self.velocities[field] = self.transitions[field].args[2].calculate_velocity(self.transitions[field].t)
            self.transitions[field].destroy()
        else:
            self.velocities[field] = 0.0
        if field in Camera.norm_fields:
            self.transitions[field] = Transition(
                self.pan_field_instant,self,field,
                Transition.Method(method, duration, GetCameraField(field), value,self.velocities[field], 0.0),
                Periodic.period
            )
        else:
            self.transitions[field] = Transition(
                self.pan_field_instant,self,field,
                Transition.MethodRad(method, duration, GetCameraField(field) * bj_RADTODEG, value, self.velocities[field], 0.0),
                Periodic.period
            )
        return self
    def pan_to(self,x,y,duration,method='smooth'):
        if method == 'instant' or duration <= Periodic.period:
            self.transitions['xy'].destroy()
            self.pan_to_instant(x,y)
            return self
        if 'xy' in self.transitions:
            self.velocities['x'] = self.transitions['xy'].args[1].calculate_velocity(self.transitions['xy'].t)
            self.velocities['y'] = self.transitions['xy'].args[2].calculate_velocity(self.transitions['xy'].t)
            self.transitions['xy'].destroy()
        else:
            self.velocities['x'] = 0.0
            self.velocities['y'] = 0.0
        self.transitions['xy'] = Transition(
            self.pan_to_instant,self,
            Transition.Method(method, duration, GetCameraTargetPositionX(), x, self.velocities['x'], 0.0),
            Transition.Method(method, duration, GetCameraTargetPositionY(), y, self.velocities['y'], 0.0),
            Periodic.period
        )
        return self
    def pan_to_setup(self,setup,duration,method='smooth'):
        if method == 'instant' or duration <= 0.01:
            for key in self.transitions:
                self.transitions[key].destroy()
            CameraSetupApplyForceDuration(setup,True,duration)
            return self
        self.pan_to(CameraSetupGetDestPositionX(setup),CameraSetupGetDestPositionY(setup),duration,method)
        self.pan_z(CameraSetupGetField(setup, CAMERA_FIELD_ZOFFSET),duration,method)
        for field in Camera.norm_fields:
            self.pan_field(field,CameraSetupGetField(setup, field),duration,method)
        for field in Camera.ang_fields:
            self.pan_field(field, CameraSetupGetField(setup, field),duration,method)
        return self
