from index import *
from event import *
from unit import *

class SpellEvent:
    _events = {}
    @staticmethod
    def get():
        id = GetSpellAbilityId()
        if id in SpellEvent._events:
            return SpellEvent._events[id]
        return None
    def __new__(cls,ability_id):
        if ability_id in SpellEvent._events:
            return SpellEvent._events[ability_id]
        o = object.__new__()
        SpellEvent._events[ability_id] = o
        return o

    @staticmethod
    def _init():
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_EFFECT,"on_effects",SpellEvent.get,Unit.get_caster)


AddScriptHook(SpellEvent._init,MAIN_BEFORE)

