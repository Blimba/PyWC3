from handle import *
from ..df.commonj import *
from compatibility import *
import math

"""
not implementing:
ConvertUnitState
ConvertPlayerUnitEvent
ConvertUnitEvent
ConvertUnitType
ConvertUnitIntegerField
ConvertUnitRealField
ConvertUnitBooleanField
ConvertUnitStringField
ConvertUnitWeaponIntegerField
ConvertUnitWeaponRealField
ConvertUnitWeaponBooleanField
ConvertUnitWeaponStringField
ConvertUnitCategory

GroupEnumUnitsOfTypeCounted
GroupEnumUnitsInRectCounted
GroupEnumUnitsInRangeOfLoc
GroupEnumUnitsInRangeCounted
GroupEnumUnitsInRangeOfLocCounted


"""


class UnitWeapon:
    def __init__(self,unit,index):
        self.parent = unit
        self.index = index
    @property
    def base_damage(self):
        return BlzGetUnitBaseDamage(self.unit, self.index)
    @base_damage.setter
    def base_damage(self,dmg):
        BlzSetUnitBaseDamage(self.unit, dmg, self.index)

    @property
    def dice_number(self):
        return BlzGetUnitDiceNumber(self.unit, self.index)
    @dice_number.setter
    def dice_number(self,dn):
        BlzSetUnitDiceNumber(self.unit, dn, self.index)

    @property
    def dice_sides(self):
        return BlzGetUnitDiceSides(self.unit, self.index)
    @dice_sides.setter
    def dice_sides(self,sides):
        BlzSetUnitDiceSides(self.unit, sides, self.index)

    @property
    def cooldown(self):
        return BlzGetUnitAttackCooldown(self.unit, self.index)
    @cooldown.setter
    def cooldown(self,cd):
        BlzSetUnitAttackCooldown(self.unit, cd, self.index)

    ## implement fields

class UnitAbility:
    def __init__(self,unit,id):
        self.parent = unit
        self.id = id
        self.ability = BlzGetUnitAbility(self._handle, id)

    @property
    def level(self):
        return GetUnitAbilityLevel(self.parent, self.id)
    @level.setter
    def level(self,lvl):
        SetUnitAbilityLevel(self.parent, self.id, lvl)

    @property
    def cooldown(self):
        return BlzGetUnitAbilityCooldown(self.parent, self.id, self.level)
    @cooldown.setter
    def cooldown(self,cooldown):
        BlzSetUnitAbilityCooldown(self.parent, self.id, self.level, cooldown)

    @property
    def cooldown_remaining(self):
        return BlzGetUnitAbilityCooldownRemaining(self.parent, self.id)

    @property
    def mana_cost(self):
        return BlzGetUnitAbilityManaCost(self.parent, self.id, self.level)
    @mana_cost.setter
    def mana_cost(self,cost):
        BlzSetUnitAbilityManaCost(self.parent, self.id, self.level, cost)

    # implement all the ability things, possibly have the ability a separate class?

class Unit(Handle):
    _loc = Location(0,0)
    _grp = CreateGroup()
    def __init__(self, playerid, unitid=0, x=0, y=0, face = 0, skinid = None):
        if isinstance(playerid, int):
            if isinstance(unitid, str):
                unitid = FourCC(unitid)
            if (skinid != None):
                Handle.__init__(self, BlzCreateUnitWithSkin, Player(playerid), unitid, x, y, face, skinid)
            else:
                Handle.__init__(self, CreateUnit, Player(playerid), unitid, x, y, face)
        else: # assume a unit, or a simple unit returning function (e.g., GetTriggerUnit) is passed.
            Handle.__init__(self, playerid)
        self._scale = 1.0
        self._timescale = 1.0
    def destroy(self):
        self.lose()
        RemoveUnit(self._handle)

    # use classes for indexed / id'd things
    # e.g.:
    # abil = unitinstance.ability(FourCC('A001'))
    # abil.level = 3
    # abil.cooldown = 2.5
    def ability(self,id):
        return UnitAbility(self._handle,id)

    def weapon(self,index):
        return UnitWeapon(self._handle,index)

    # order functions
    def order(self, o, *args):
        if len(args) == 0:
            IssueImmediateOrder(self._handle, o)
        elif len(args) == 1:
            IssueTargetOrder(self._handle, o, args[0])
        elif len(args) == 2:
            IssuePointOrder(self._handle, o, args[0], args[1])

    # unit lists (removes need for groups)
    @staticmethod
    def _list(enum,*args):
        lst = []
        enum(Unit._grp, *args)
        u = FirstOfGroup(Unit._grp)
        while u != None:
            lst.append(Unit.get(u) or Unit(u))
            GroupRemoveUnit(Unit._grp, u)
            u = FirstOfGroup(Unit._grp)
        return lst
    @staticmethod
    def list_type(id,filter=None):
        return Unit._list(GroupEnumUnitsOfType,UnitId2String(id),filter)
    @staticmethod
    def list_player(playerid,filter=None):
        return Unit._list(GroupEnumUnitsOfPlayer, Player(playerid), filter)
    @staticmethod
    def list_in_range(x,y,range,filter=None):
        return Unit._list(GroupEnumUnitsInRange,x,y,range,filter)
    @staticmethod
    def list_in_rect(rect,filter=None):
        return Unit._list(GroupEnumUnitsInRect,rect,filter)
    @staticmethod
    def list_selected(playerid,filter=None):
        return Unit._list(GroupEnumUnitsSelected,Player(playerid),filter)

    # simple actions
    def kill(self):
        KillUnit(self._handle)

    def player_color(self,playerid):
        SetUnitColor(self._handle,ConvertPlayerColor(playerid))

    def color(self, r, g, b, a=255):
        SetUnitVertexColor(self._handle, r, g, b, a)

    def is_visible_for_player(self,playerid):
        return IsUnitVisible(self._handle,Player(playerid))

    def animate(self,animation):
        if isinstance(animation,str):
            SetUnitAnimation(self._handle, animation)
        elif isinstance(animation, int):
            SetUnitAnimationByIndex(self._handle, animation)


    # triggering



    # manual properties

    @property
    def level(self):
        return GetUnitLevel(self._handle)

    @property
    def owner(self):
        return GetOwningPlayer(self._handle)

    @owner.setter
    def owner(self,playerid):
        SetUnitOwner(self._handle, Player(playerid), True)



    @property
    def move_speed(self):
        return GetUnitMoveSpeed(self._handle)

    @move_speed.setter
    def move_speed(self,newspeed):
        SetUnitMoveSpeed(self._handle, newspeed)

    @property
    def face(self):
        return GetUnitFacing(self._handle)

    @face.setter
    def face(self,newface):
        SetUnitFacingTimed(self._handle, newface, 0.01)  # consider this immediate

    @property
    def name(self):
        return GetUnitName(self._handle)

    @name.setter
    def name(self,newname):
        return BlzSetUnitName(self._handle, newname)

    @property
    def type(self):
        return GetUnitTypeId(self._handle)

    @property
    def paused(self):
        return IsUnitPaused(self._handle)

    @paused.setter
    def paused(self,p):
        BlzPauseUnitEx(self._handle,p)

    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self,newscale):
        self._scale = newscale
        SetUnitScale(self._handle, newscale, newscale, newscale)

    @property
    def timescale(self):
        return self._timescale

    @timescale.setter
    def timescale(self, newtimescale):
        self._timescale = newtimescale
        SetUnitTimeScale(self._handle, newtimescale, newtimescale, newtimescale)

    @property
    def x(self):
        return GetUnitX(self._handle)

    @x.setter
    def x(self, x):
        SetUnitX(self._handle, x)

    @property
    def y(self):
        return GetUnitY(self._handle)

    @y.setter
    def y(self, y):
        SetUnitY(self._handle, y)

    @property
    def z(self):
        return BlzGetUnitZ(self._handle)

    @z.setter
    def z(self, z):
        MoveLocation(Unit._loc, GetUnitX(self._handle), GetUnitY(self._handle))
        SetUnitFlyHeight(self._handle, z-GetLocationZ(Unit._loc), 0.0)  # test if 0 works

    def set_position(self,x,y,z):
        SetUnitX(self._handle,x)
        SetUnitY(self._handle,y)
        MoveLocation(Unit._loc, x, y)
        SetUnitFlyHeight(self._handle, z - GetLocationZ(Unit._loc), 0.0)  # test if 0 works

    def look_along(self,x,y,z,bone="chest"):
        SetUnitLookAt(self._handle,bone,self._handle,x,y,z)


    # Automatically generated get unit functions
    @staticmethod
    def get_filter():
        return Handle.get(GetFilterUnit()) or Unit(GetFilterUnit)

    @staticmethod
    def get_enum():
        return Handle.get(GetEnumUnit()) or Unit(GetEnumUnit)

    @staticmethod
    def get_entering():
        return Handle.get(GetEnteringUnit()) or Unit(GetEnteringUnit)

    @staticmethod
    def get_leaving():
        return Handle.get(GetLeavingUnit()) or Unit(GetLeavingUnit)

    @staticmethod
    def get_leveling():
        return Handle.get(GetLevelingUnit()) or Unit(GetLevelingUnit)

    @staticmethod
    def get_learning():
        return Handle.get(GetLearningUnit()) or Unit(GetLearningUnit)

    @staticmethod
    def get_revivable():
        return Handle.get(GetRevivableUnit()) or Unit(GetRevivableUnit)

    @staticmethod
    def get_reviving():
        return Handle.get(GetRevivingUnit()) or Unit(GetRevivingUnit)

    @staticmethod
    def get_dying():
        return Handle.get(GetDyingUnit()) or Unit(GetDyingUnit)

    @staticmethod
    def get_killing():
        return Handle.get(GetKillingUnit()) or Unit(GetKillingUnit)

    @staticmethod
    def get_decaying():
        return Handle.get(GetDecayingUnit()) or Unit(GetDecayingUnit)

    @staticmethod
    def get_researching():
        return Handle.get(GetResearchingUnit()) or Unit(GetResearchingUnit)

    @staticmethod
    def get_trained():
        return Handle.get(GetTrainedUnit()) or Unit(GetTrainedUnit)

    @staticmethod
    def get_detected():
        return Handle.get(GetDetectedUnit()) or Unit(GetDetectedUnit)

    @staticmethod
    def get_summoning():
        return Handle.get(GetSummoningUnit()) or Unit(GetSummoningUnit)

    @staticmethod
    def get_summoned():
        return Handle.get(GetSummonedUnit()) or Unit(GetSummonedUnit)

    @staticmethod
    def get_transport():
        return Handle.get(GetTransportUnit()) or Unit(GetTransportUnit)

    @staticmethod
    def get_loaded():
        return Handle.get(GetLoadedUnit()) or Unit(GetLoadedUnit)

    @staticmethod
    def get_selling():
        return Handle.get(GetSellingUnit()) or Unit(GetSellingUnit)

    @staticmethod
    def get_sold():
        return Handle.get(GetSoldUnit()) or Unit(GetSoldUnit)

    @staticmethod
    def get_buying():
        return Handle.get(GetBuyingUnit()) or Unit(GetBuyingUnit)

    @staticmethod
    def get_changing():
        return Handle.get(GetChangingUnit()) or Unit(GetChangingUnit)

    @staticmethod
    def get_manipulating():
        return Handle.get(GetManipulatingUnit()) or Unit(GetManipulatingUnit)

    @staticmethod
    def get_ordered():
        return Handle.get(GetOrderedUnit()) or Unit(GetOrderedUnit)

    @staticmethod
    def get_order_target():
        return Handle.get(GetOrderTargetUnit()) or Unit(GetOrderTargetUnit)

    @staticmethod
    def get_spell_ability():
        return Handle.get(GetSpellAbilityUnit()) or Unit(GetSpellAbilityUnit)

    @staticmethod
    def get_spell_target():
        return Handle.get(GetSpellTargetUnit()) or Unit(GetSpellTargetUnit)

    @staticmethod
    def get_trigger():
        return Handle.get(GetTriggerUnit()) or Unit(GetTriggerUnit)

    @staticmethod
    def get_event_state():
        return Handle.get(GetEventUnitState()) or Unit(GetEventUnitState)

    @staticmethod
    def get_event_target():
        return Handle.get(GetEventTargetUnit()) or Unit(GetEventTargetUnit)

    @staticmethod
    def get_mouse_focus():
        return Handle.get(BlzGetMouseFocusUnit()) or Unit(BlzGetMouseFocusUnit)

    # Automatically generated set unit functions
    @property
    def acquire_range(self):
        return GetUnitAcquireRange(self._handle)

    @acquire_range.setter
    def acquire_range(self, newAcquireRange):
        SetUnitAcquireRange(self._handle, newAcquireRange)

    @property
    def turn_speed(self):
        return GetUnitTurnSpeed(self._handle)

    @turn_speed.setter
    def turn_speed(self, newTurnSpeed):
        SetUnitTurnSpeed(self._handle, newTurnSpeed)

    @property
    def prop_window(self):
        return GetUnitPropWindow(self._handle)

    @prop_window.setter
    def prop_window(self, newPropWindowAngle):
        SetUnitPropWindow(self._handle, newPropWindowAngle)

    @property
    def fly_height(self):
        return GetUnitFlyHeight(self._handle)

    @fly_height.setter
    def fly_height(self,height):
        SetUnitFlyHeight(self._handle,height,0.0)  # this one wasn't autogenerated because of the 0.0

    @property
    def default_acquire_range(self):
        return GetUnitDefaultAcquireRange(self._handle)

    @property
    def default_turn_speed(self):
        return GetUnitDefaultTurnSpeed(self._handle)

    @property
    def default_prop_window(self):
        return GetUnitDefaultPropWindow(self._handle)

    @property
    def default_fly_height(self):
        return GetUnitDefaultFlyHeight(self._handle)

    @property
    def point_value(self):
        return GetUnitPointValue(self._handle)

    @property
    def current_order(self):
        return GetUnitCurrentOrder(self._handle)

    @property
    def user_data(self):
        return GetUnitUserData(self._handle)

    @user_data.setter
    def user_data(self, data):
        SetUnitUserData(self._handle, data)

    @property
    def max_hp(self):  # name fixes for h_p => hp
        return BlzGetUnitMaxHP(self._handle)

    @max_hp.setter
    def max_hp(self, hp):
        BlzSetUnitMaxHP(self._handle, hp)

    @property
    def max_mana(self):
        return BlzGetUnitMaxMana(self._handle)

    @max_mana.setter
    def max_mana(self, mana):
        BlzSetUnitMaxMana(self._handle, mana)

    @property
    def armor(self):
        return BlzGetUnitArmor(self._handle)

    @armor.setter
    def armor(self, armorAmount):
        BlzSetUnitArmor(self._handle, armorAmount)

    @property
    def collision_size(self):
        return BlzGetUnitCollisionSize(self._handle)

    @property
    def skin(self):
        return BlzGetUnitSkin(self._handle)

    @skin.setter
    def skin(self, skinId):
        BlzSetUnitSkin(self._handle, skinId)
