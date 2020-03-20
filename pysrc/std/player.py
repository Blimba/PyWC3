from .index import *
from ..df.commonj import *
from ..df.blizzardj import bj_MAX_PLAYERS
from .handle import *
from .event import *

class PlayerEvent(ClassEvent):
    def __init__(self, playerevent, methodname, *args):
        ClassEvent.__init__(self, methodname, Player, *args)
        for playerid in range(bj_MAX_PLAYERS):
            if type(playerevent) == list:
                for pue in playerevent:
                    self.register(TriggerRegisterPlayerEvent, Player(playerid), pue)
            else:
                self.register(TriggerRegisterPlayerEvent, Player(playerid), playerevent)

BlzPlayer = Player
class Player:
    color = [
        "|c00ff0303",
        "|c000042ff",
        "|c001ce6b9",
        "|c00540081",
        "|c00fffc01",
        "|c00ff8000",
        "|c0020c000",
        "|c00e55bb0",
        "|c00959697",
        "|c007ebff1",
        "|c00106246",
        "|c004e2a04",
    ]
    def __new__(cls,i):
        return BlzPlayer(i)

    @staticmethod
    def on_leave(p):
        print(Player.color[GetPlayerId(p)] + GetPlayerName(p) + "|r has left the game.")

    @staticmethod
    def _init():
        PlayerEvent(EVENT_PLAYER_LEAVE, "on_leave", GetTriggerPlayer)
        PlayerEvent(EVENT_PLAYER_END_CINEMATIC, "on_escape", GetTriggerPlayer)


AddScriptHook(Player._init, MAIN_BEFORE)