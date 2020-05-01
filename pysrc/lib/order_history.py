from ..std.event import Event
from ..std.index import *
from ..std.unit import *
from .mouseevent import MouseEvent
class OrderHistory:
    history = 5

    @staticmethod
    def _repeat(unit,index=-1):
        o = unit.order_list[index]
        if o['type'] == 'point':
            unit.order(o['orderid'],o['x'],o['y'])
        elif o['type'] == 'target':
            unit.order(o['orderid'],o['target'])
        else:
            unit.order(o['orderid'])

    @staticmethod
    def _point(e,unit):
        order_id = GetIssuedOrderId()
        if OrderHistory.active:
            if Handle.get(GetOrderedUnit()):
                unit = unit()
                if unit.order_list == None:
                    OrderHistory._unit_setup(unit)
                unit.order_list.append({'type':'point','orderid':order_id,'orderstring':OrderId2String(order_id),'x':GetOrderPointX(),'y':GetOrderPointY()})
                if len(unit.order_list) > OrderHistory.history:
                    unit.order_list.pop(0)

    @staticmethod
    def _target(e,unit):
        order_id = GetIssuedOrderId()
        if OrderHistory.active:
            if Handle.get(GetOrderedUnit()):
                unit = unit()
                if unit.order_list == None:
                    OrderHistory._unit_setup(unit)
                unit.order_list.append({'type':'target','orderid':order_id,'orderstring':OrderId2String(order_id),'target':GetOrderTarget()})
                if len(unit.order_list) > OrderHistory.history:
                    unit.order_list.pop(0)

    @staticmethod
    def _immediate(e,unit):
        order_id = GetIssuedOrderId()
        if OrderHistory.active:
            if Handle.get(GetOrderedUnit()):
                unit = unit()
                if unit.order_list == None:
                    OrderHistory._unit_setup(unit)
                unit.order_list.append({'type':'immediate','orderid':order_id,'orderstring':OrderId2String(order_id)})
                if len(unit.order_list) > OrderHistory.history:
                    unit.order_list.pop(0)

    @staticmethod
    def _unit_setup(unit):
        unit.order_list = []
        unit.last_order = 0
        unit.was_idle = lambda self: self.last_order == 0
        unit.repeat_order = OrderHistory._repeat
    @staticmethod
    def _click(e):
        if BlzGetTriggerPlayerMouseX() != 0.0 or BlzGetTriggerPlayerMouseY() != 0.0:
            GroupEnumUnitsSelected(OrderHistory._g,GetTriggerPlayer())
            u = FirstOfGroup(OrderHistory._g)
            while(u!=None):
                if Handle.get(u):
                    Unit.get(u).last_order = GetUnitCurrentOrder(u)
                GroupRemoveUnit(OrderHistory._g,u)
                u = FirstOfGroup(OrderHistory._g)

    _g = None
    def __init__(self):
        OrderHistory._g = CreateGroup()
        Unit.suspend_events()
        pe = Event(OrderHistory._point,Unit.get_ordered)
        te = Event(OrderHistory._target,Unit.get_ordered)
        ie = Event(OrderHistory._immediate,Unit.get_ordered)
        me = Event(OrderHistory._click)
        for i in range(bj_MAX_PLAYERS):
            pe.register(TriggerRegisterPlayerUnitEvent, Player(i), EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER)
            te.register(TriggerRegisterPlayerUnitEvent, Player(i), EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER)
            ie.register(TriggerRegisterPlayerUnitEvent, Player(i), EVENT_PLAYER_UNIT_ISSUED_ORDER)
            me.register(TriggerRegisterPlayerEvent, Player(i), EVENT_PLAYER_MOUSE_DOWN)
        Unit.resume_events()
    active=True
    @staticmethod
    def init():
        OrderHistory.active = True


AddScriptHook(OrderHistory,MAIN_BEFORE)
