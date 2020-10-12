from ..std.index import *
from ..df.commonj import *
from ..df.blizzardj import bj_MAX_PLAYERS
from ..std.timer import *
class MouseEvent:
    timer = None
    _lst = []
    _events = 0
    _active = False
    def __init__(self, callback, *args):
        self.callback = callback
        self.args = args
        MouseEvent._lst.append(self)

    @staticmethod
    def _timeout():
        MouseEvent._events -= 1
        if MouseEvent._events >= 1:
            print('Double mouse event ({} events)!'.format(MouseEvent._events))
        for me in MouseEvent._lst:
            me.callback(*me.args)

    @staticmethod
    def _click():
        # clicking anywhere apart from on the map gives 0.0 0.0 as coordinates
        if MouseEvent._active and (BlzGetTriggerPlayerMouseX() != 0.0 or BlzGetTriggerPlayerMouseY() != 0.0):
            MouseEvent._events += 1
            if MouseEvent._events > 1 and GetTriggerPlayer() != MouseEvent.player:
                print('Two player mouse event ({} events), Player {} ignored!'.format(MouseEvent._events,GetPlayerId(GetTriggerPlayer())))
            if MouseEvent._events == 1:
                MouseEvent.x = BlzGetTriggerPlayerMouseX()
                MouseEvent.y = BlzGetTriggerPlayerMouseY()
                MouseEvent.button = BlzGetTriggerPlayerMouseButton()
                MouseEvent.player = GetTriggerPlayer()

                MouseEvent.timer.start(0.0, MouseEvent._timeout)
                MouseEvent.focus_unit = BlzGetMouseFocusUnit()
                MouseEvent.unit_order = None
                MouseEvent.ordered_unit = None
            else:
                MouseEvent._events -= 1

    @staticmethod
    def _ordered():
        if MouseEvent._active and MouseEvent._events == 1:
            MouseEvent.unit_order = GetIssuedOrderId()
            MouseEvent.ordered_unit = GetOrderedUnit()

    @staticmethod
    def _make_triggers():
        t = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            TriggerRegisterPlayerEvent(t, Player(i), EVENT_PLAYER_MOUSE_DOWN)
        TriggerAddAction(t,MouseEvent._click)

        t = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            TriggerRegisterPlayerUnitEvent(t,Player(i),EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER, None)
        TriggerAddAction(t,MouseEvent._ordered)
        MouseEvent._active = True
        MouseEvent.timer = Timer()

    @staticmethod
    def suspend_events():
        MouseEvent._active = False

    @staticmethod
    def resume_events():
        MouseEvent._active = True

AddScriptHook(MouseEvent._make_triggers, MAIN_BEFORE)