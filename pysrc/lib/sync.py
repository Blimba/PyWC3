from ..std.index import *
from ..df.blizzardj import bj_MAX_PLAYERS

class NumberSync:
    id = 0
    instances = {}
    def __init__(self,player,callback,*args):
        NumberSync.id += 1
        syncstr = str(NumberSync.id)+","+",".join(args)
        NumberSync.instances[str(NumberSync.id)]=self
        self.callback = callback
        if player == GetLocalPlayer():
            BlzSendSyncData("sync",syncstr)

    @staticmethod
    def _on_sync():
        syncstr = BlzGetTriggerSyncData()
        data = syncstr.split(",")
        self = NumberSync.instances[data[0]]
        del NumberSync.instances[data[0]]
        args = []
        for d in data[1:]:
            args.append(float(d))
        self.data = args
        self.callback(*args)
    @staticmethod
    def _init():
        t = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            BlzTriggerRegisterPlayerSyncEvent(t, Player(i), "sync", False)
        TriggerAddAction(t, NumberSync._on_sync)

AddScriptHook(NumberSync._init)