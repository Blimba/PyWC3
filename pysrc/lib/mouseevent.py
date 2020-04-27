from ..std.index import *
from ..df.commonj import *
from ..df.blizzardj import bj_MAX_PLAYERS
from ..std.timer import *
class MouseEvent:
    timer = None
    _lst = []

    def __init__(self, callback, *args):
        self.callback = callback
        self.args = args
        MouseEvent._lst.append(self)

    @staticmethod
    def _timeout():
        for me in MouseEvent._lst:
            me.callback(*me.args)

    @staticmethod
    def _click():
        # clicking anywhere apart from on the map gives 0.0 0.0 as coordinates
        if BlzGetTriggerPlayerMouseX() != 0.0 and BlzGetTriggerPlayerMouseY() != 0.0:
            MouseEvent.x = BlzGetTriggerPlayerMouseX()
            MouseEvent.y = BlzGetTriggerPlayerMouseY()
            MouseEvent.button = BlzGetTriggerPlayerMouseButton()
            MouseEvent.player = GetTriggerPlayer()
            MouseEvent.timer.start(0.0, MouseEvent._timeout)
            MouseEvent.focus_unit = BlzGetMouseFocusUnit()
            MouseEvent.unit_order = None
            MouseEvent.ordered_unit = None

    @staticmethod
    def _ordered():
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

        MouseEvent.timer = Timer()


AddScriptHook(MouseEvent._make_triggers, MAIN_BEFORE)