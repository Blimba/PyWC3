from .unit import *


class Item(Handle):
    def __init__(self, itemid, x=0, y=0, skinid=None):
        if isinstance(itemid, str):
            itemid = FourCC(itemid)
        if isinstance(itemid, int):
            if (skinid != None):
                Handle.__init__(self, BlzCreateItemWithSkin(itemid,x,y,skinid))
            else:
                Handle.__init__(self, CreateItem(itemid, x, y))
        else: # assume an item is passed
            Handle.__init__(self, itemid)
    def destroy(self):
        RemoveItem(self._handle)

    @property
    def type(self):
        return GetItemTypeId(self._handle)

    @staticmethod
    def get_manipulated():
        return Item.get(GetManipulatedItem())

    @property
    def x(self):
        return GetItemX(self._handle)

    @property
    def y(self):
        return GetItemY(self._handle)

    def set_position(self,x,y):
        SetItemPosition(self._handle,x,y)

    @staticmethod
    def _init():
        PlayerUnitEvent(EVENT_PLAYER_UNIT_PICKUP_ITEM, "on_pickup", Item.get_manipulated, Unit.get_manipulating)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_DROP_ITEM, "on_drop", Item.get_manipulated, Unit.get_manipulating)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_PAWN_ITEM, "on_pawn", Item.get_manipulated, Unit.get_manipulating)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SELL_ITEM, "on_sell", Item.get_manipulated, Unit.get_manipulating)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_USE_ITEM, "on_use", Item.get_manipulated, Unit.get_manipulating)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_STACK_ITEM, "on_stack", Item.get_manipulated, Unit.get_manipulating)

AddScriptHook(Item._init)