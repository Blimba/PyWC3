"""

    An easy event for spells.

    Usage:

    def ability_cast(se, caster):
        print(caster,'cast spell A001')
    se = SpellEvent(b'A001')  # replace A001 with your ability code
    se.on_cast = ability_cast

    All events are equally available:

    - on_cast (corresponds to EVENT_PLAYER_UNIT_SPELL_CAST)
    - on_channel (corresponds to EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    - on_finish (corresponds to EVENT_PLAYER_UNIT_SPELL_FINISH)
    - on_endcast (corresponds to EVENT_PLAYER_UNIT_SPELL_ENDCAST)
    - on_effects (corresponds to EVENT_PLAYER_UNIT_SPELL_EFFECT)

    Be advised that only 1 SpellEvent instance of the same ability may exist.

"""

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
        o = object.__new__(cls)
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

