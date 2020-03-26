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
        # PlayerUnitEvent is defined in unit.py
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_CAST, "on_cast", SpellEvent.get, Unit.get_caster)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_CHANNEL, "on_channel", SpellEvent.get, Unit.get_caster)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_FINISH, "on_finish", SpellEvent.get, Unit.get_caster)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_ENDCAST, "on_endcast", SpellEvent.get, Unit.get_caster)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_SPELL_EFFECT, "on_effects", SpellEvent.get,Unit.get_caster)


AddScriptHook(SpellEvent._init,MAIN_BEFORE)

