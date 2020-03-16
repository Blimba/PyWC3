from ..df.blizzardj import bj_MAX_PLAYERS
from ..df.commonj import *
from .math3d import Vector3
from ..std.index import *
import math


class Camera:
    _id = 0
    def __init__(self):
        self.id = Camera._id
        Camera._cameras[str(Camera._id)] = self
        Camera._id += 1

    def __str__(self):
        return "Camera"+str(self.id)+":"+str(self.target)+":"+str(self.source)

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
        del Camera._cameras[str(self.id)]
        self.callback(*self.args)

    @staticmethod
    def _make_triggers():
        t = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            BlzTriggerRegisterPlayerSyncEvent(t, Player(i), "camerasync", False)
        TriggerAddAction(t, Camera._on_sync)
        Camera._cameras = {}


    def sync_from_player(self,player,callback,*args):
        self.callback = callback
        self.args = args
        if isinstance(player, int):
            player = Player(player)
        if player == GetLocalPlayer():
            # careful: asynchronous execution!
            syncstr = str(self.id)+","+str(GetCameraTargetPositionX())+","+str(GetCameraTargetPositionY())+","+str(GetCameraTargetPositionZ())+","+str(GetCameraEyePositionX())+","+str(GetCameraEyePositionY())+","+str(GetCameraEyePositionZ())
            BlzSendSyncData("camerasync", syncstr)

AddScriptHook(Camera._make_triggers, MAIN_BEFORE)