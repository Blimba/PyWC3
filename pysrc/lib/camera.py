from ..df.blizzardj import bj_MAX_PLAYERS
from ..df.commonj import *
from .math3d import Vector3
from ..std.index import *
from .transition import *
import math


class Camera:
    _id = 0
    _cameras = {}
    def __init__(self):
        self.source = None
        self.target = None

    def __str__(self):
        return "Camera:"+str(self.target)+":"+str(self.source)

    @staticmethod
    def from_id(id):
        return Camera._cameras[str(id)]

    @staticmethod
    def _on_sync():
        # camera on sync called
        syncstr = BlzGetTriggerSyncData()
        d = syncstr.split(",")
        id = str(d[0])
        self = Camera.from_id(id)
        self.target = Vector3(float(d[1]),float(d[2]),float(d[3]),True)
        self.source = Vector3(float(d[4]),float(d[5]),float(d[6]),True)
        self._set_properties()
        del Camera._cameras[str(self.id)]
        self.callback(*self.args)

    @staticmethod
    def _make_triggers():
        t = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            BlzTriggerRegisterPlayerSyncEvent(t, Player(i), "camerasync", False)
        TriggerAddAction(t, Camera._on_sync)


    def sync_from_player(self,player,callback,*args):
        self.callback = callback
        self.args = args
        self.id = Camera._id
        Camera._cameras[str(Camera._id)] = self
        Camera._id += 1
        if isinstance(player, int):
            player = Player(player)
        if player == GetLocalPlayer():
            # careful: asynchronous execution!
            syncstr = str(self.id)+","+str(GetCameraTargetPositionX())+","+str(GetCameraTargetPositionY())+","+str(GetCameraTargetPositionZ())+","+str(GetCameraEyePositionX())+","+str(GetCameraEyePositionY())+","+str(GetCameraEyePositionZ())
            BlzSendSyncData("camerasync", syncstr)

    def from_local(self):
        self.target = Vector3(GetCameraTargetPositionX(),GetCameraTargetPositionY(),GetCameraTargetPositionZ(),True)
        self.source = Vector3(GetCameraEyePositionX(),GetCameraEyePositionY(),GetCameraEyePositionZ(),True)
        self._set_properties()
        return self

    def _set_properties(self):
        v = self.target-self.source
        self.dist = len(v)
        xy = math.sqrt(v.x*v.x+v.y*v.y)
        self.pitch = Atan2(v.z, xy)
        self.yaw = Atan2(v.y, v.x)


    def from_setup(self,setup):
        x = CameraSetupGetDestPositionX(setup)
        y = CameraSetupGetDestPositionY(setup)
        self.target = Vector3.from_terrain(x,y,True)
        self.target.z += CameraSetupGetField(setup,CAMERA_FIELD_ZOFFSET)
        yaw = -CameraSetupGetField(setup,CAMERA_FIELD_ROTATION)  # in degrees
        self.yaw = yaw
        pitch = -CameraSetupGetField(setup,CAMERA_FIELD_ANGLE_OF_ATTACK)  # in degrees
        self.pitch = pitch
        dist = CameraSetupGetField(setup,CAMERA_FIELD_TARGET_DISTANCE)
        self.dist = dist
        eyex = -math.cos(yaw*bj_DEGTORAD)*math.cos(pitch*bj_DEGTORAD)*dist+x
        eyey = math.sin(yaw*bj_DEGTORAD)*math.cos(pitch*bj_DEGTORAD)*dist+y
        eyez = math.sin(pitch*bj_DEGTORAD)*dist + CameraSetupGetField(setup,CAMERA_FIELD_ZOFFSET)
        self.source = Vector3(eyex,eyey,eyez)

        # self.roll = CameraSetupGetField(setup,CAMERA_FIELD_ROLL)  # in degrees
        # self.fov = CameraSetupGetField(setup,CAMERA_FIELD_FIELD_OF_VIEW)
        # self.farz = CameraSetupGetField(setup,CAMERA_FIELD_FARZ)

        return self

    transitions = {}
    velocities = {}
    norm_fields = [CAMERA_FIELD_TARGET_DISTANCE, CAMERA_FIELD_FARZ]
    ang_fields = [CAMERA_FIELD_ANGLE_OF_ATTACK, CAMERA_FIELD_ROTATION]

    @staticmethod
    def _set_z(z):
        SetCameraField(CAMERA_FIELD_ZOFFSET, z, - 0.01)
        SetCameraField(CAMERA_FIELD_ZOFFSET, z, 0.01)

    @staticmethod
    def apply_setup(setup,duration,method='smooth'):
        c = Camera().from_setup(setup)
        if 'xy' in Camera.transitions:
            Camera.velocities['x'] = Camera.transitions['xy'].args[0].calculate_velocity(Camera.transitions['xy'].t)
            Camera.velocities['y'] = Camera.transitions['xy'].args[1].calculate_velocity(Camera.transitions['xy'].t)
            Camera.transitions['xy'].destroy()
        else:
            Camera.velocities['x'] = 0.0
            Camera.velocities['y'] = 0.0
        if 'z' in Camera.transitions:
            Camera.velocities['z'] = Camera.transitions['z'].args[0].calculate_velocity(Camera.transitions['z'].t)
            Camera.transitions['z'].destroy()
        else:
            Camera.velocities['z'] = 0.0
        for field in Camera.norm_fields:
            if field in Camera.transitions:
                Camera.velocities[field] = Camera.transitions[field].args[1].calculate_velocity(Camera.transitions[field].t)
                Camera.transitions[field].destroy()
            else:
                Camera.velocities[field] = 0.0
        for field in Camera.ang_fields:
            if field in Camera.transitions:
                Camera.velocities[field] = Camera.transitions[field].args[1].calculate_velocity(Camera.transitions[field].t)
                Camera.transitions[field].destroy()
            else:
                Camera.velocities[field] = 0.0
        if method == 'smooth':
            Camera.transitions['xy'] = Transition(
                PanCameraToTimed,
                Transition.Smooth_Acceleration(duration, GetCameraTargetPositionX(), c.target.x, Camera.velocities['x'], 0.0),
                Transition.Smooth_Acceleration(duration, GetCameraTargetPositionY(), c.target.y, Camera.velocities['y'], 0.0),
                Periodic.period
            )
            Camera.transitions['z'] = Transition(
                Camera._set_z,
                Transition.Smooth_Acceleration(duration,GetCameraField(CAMERA_FIELD_ZOFFSET),CameraSetupGetField(setup, CAMERA_FIELD_ZOFFSET), Camera.velocities['z'], 0.0),
            )
            for field in Camera.norm_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Smooth_Acceleration(duration, GetCameraField(field), CameraSetupGetField(setup, field), Camera.velocities[field] , 0.0),
                    Periodic.period
                )
            for field in Camera.ang_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Smooth_Acceleration_Angular(duration, GetCameraField(field)*bj_RADTODEG, CameraSetupGetField(setup, field), Camera.velocities[field], 0.0),
                    Periodic.period
                )
        elif method == 'split':
            Camera.transitions['xy'] = Transition(
                PanCameraToTimed,
                Transition.Split_Acceleration(duration, GetCameraTargetPositionX(), c.target.x, Camera.velocities['x'], 0.0),
                Transition.Split_Acceleration(duration, GetCameraTargetPositionY(), c.target.y, Camera.velocities['y'], 0.0),
                Periodic.period
            )
            Camera.transitions['z'] = Transition(
                Camera._set_z,
                Transition.Split_Acceleration(duration,GetCameraField(CAMERA_FIELD_ZOFFSET),CameraSetupGetField(setup, CAMERA_FIELD_ZOFFSET), Camera.velocities['z'], 0.0),
            )
            for field in Camera.norm_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Split_Acceleration(duration, GetCameraField(field), CameraSetupGetField(setup, field), Camera.velocities[field] , 0.0),
                    Periodic.period
                )
            for field in Camera.ang_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Split_Acceleration_Angular(duration, GetCameraField(field)*bj_RADTODEG, CameraSetupGetField(setup, field), Camera.velocities[field], 0.0),
                    Periodic.period
                )
        elif method == 'constant':
            Camera.transitions['xy'] = Transition(
                PanCameraToTimed,
                Transition.Constant_Acceleration(duration, GetCameraTargetPositionX(), c.target.x, Camera.velocities['x']),
                Transition.Constant_Acceleration(duration, GetCameraTargetPositionY(), c.target.y, Camera.velocities['y']),
                Periodic.period
            )
            Camera.transitions['z'] = Transition(
                Camera._set_z,
                Transition.Constant_Acceleration(duration,GetCameraField(CAMERA_FIELD_ZOFFSET),CameraSetupGetField(setup, CAMERA_FIELD_ZOFFSET), Camera.velocities['z']),
            )
            for field in Camera.norm_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Constant_Acceleration(duration, GetCameraField(field), CameraSetupGetField(setup, field), Camera.velocities[field]),
                    Periodic.period
                )
            for field in Camera.ang_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Constant_Acceleration_Angular(duration, GetCameraField(field)*bj_RADTODEG, CameraSetupGetField(setup, field), Camera.velocities[field]),
                    Periodic.period
                )
        elif method == 'linear':
            Camera.transitions['xy'] = Transition(
                PanCameraToTimed,
                Transition.Linear(duration, GetCameraTargetPositionX(), c.target.x),
                Transition.Linear(duration, GetCameraTargetPositionY(), c.target.y),
                Periodic.period
            )
            Camera.transitions['z'] = Transition(
                Camera._set_z,
                Transition.Linear(duration,GetCameraField(CAMERA_FIELD_ZOFFSET),CameraSetupGetField(setup, CAMERA_FIELD_ZOFFSET)),
            )
            for field in Camera.norm_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Linear(duration, GetCameraField(field), CameraSetupGetField(setup, field)),
                    Periodic.period
                )
            for field in Camera.ang_fields:
                Camera.transitions[field] = Transition(
                    SetCameraField,
                    field,
                    Transition.Linear_Angular(duration, GetCameraField(field)*bj_RADTODEG, CameraSetupGetField(setup, field)),
                    Periodic.period
                )




AddScriptHook(Camera._make_triggers, MAIN_BEFORE)