from handle import *
from ..df.commonj import *
from compatibility import *
from ..df.blizzardj import bj_MAX_PLAYERS
from index import *
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

UnitStripHeroLevel
UnitModifySkillPoints
DecUnitAbilityLevel
IncUnitAbilityLevel
SetUnitExploded
SetUnitInvulnerable
GetUnitPointValueByType
UnitAddItemById
UnitHasItem
UnitDropItemSlot
GetUnitLoc
GetUnitDefaultMoveSpeed
GetUnitRallyPoint
GetUnitRallyUnit
GetUnitRallyDestructable
IsUnitInGroup
IsUnitInForce
IsUnitOwnedByPlayer
IsUnitDetected
IsUnitFogged
IsUnitMasked
IsUnitInRange
IsUnitInRangeXY
IsUnitInRangeLoc
IsHeroUnitId
IsUnitIdType
AddUnitToAllStock
AddUnitToStock
RemoveUnitFromAllStock
RemoveUnitFromStock
SetAllUnitTypeSlots
SetUnitTypeSlots
GetPlayerUnitCount
GetPlayerTypedUnitCount
SetPlayerUnitsOwner
StoreUnit					
SyncStoredUnit
HaveStoredUnit					
FlushStoredUnit					
RestoreUnit					
SaveUnitHandle				
SaveUnitPoolHandle			
LoadUnitHandle			
LoadUnitPoolHandle		
CreateUnitPool
DestroyUnitPool
UnitPoolAddUnitType
UnitPoolRemoveUnitType
PlaceRandomUnit
SetUnitFog
CreateMinimapIconOnUnit
SetTextTagPosUnit
AttachSoundToUnit

GroupAddUnit
BlzGroupUnitAt
IsUnitInRegion

CreateUnitByName
CreateUnitAtLoc
CreateUnitAtLocByName
SetUnitPosition
SetUnitPositionLoc
SetUnitFacingTimed
SetUnitCreepGuard


BlzGetLocalUnitZ
"""

class PlayerUnitEvent(Handle):
    @staticmethod
    def _triggered():
        self = Handle.get(GetTriggeringTrigger())
        nargs = []
        for arg in self.args:
            if callable(arg):
                nargs.append(arg())
        if callable(getattr(nargs[0],self.callback)):
            try: getattr(nargs[0],self.callback)(*nargs)
            except: print(Error)

    def __init__(self, playerunitevent, callback, *args):
        Handle.__init__(self,CreateTrigger)
        self.callback = callback
        self.args = args  # these are the event units that should be called!
        for playerid in range(bj_MAX_PLAYERS):
            if type(playerunitevent) == list:
                for pue in playerunitevent:
                    TriggerRegisterPlayerUnitEvent(self._handle, Player(playerid), pue, None)
            else:
                TriggerRegisterPlayerUnitEvent(self._handle, Player(playerid), playerunitevent, None)
        TriggerAddAction(self._handle, PlayerUnitEvent._triggered)

class UnitInventory:
    def __init__(self,unit):
        self._items = []
        self._unit = unit
        self._size = UnitInventorySize(self._unit._handle)
        for i in range(self._size):
            self._items.append(UnitItemInSlot(self._unit._handle, i))

    def get(self,item):
        if isinstance(item, int) and item < self._size:
            return self._items[item]
        return None

    def set(self, key, value):
        if isinstance(key, int) and key < self._size:
            UnitAddItemToSlotById(value)

    def __contains__(self, item):
        return item in self._items

    def list_type(self,itemtype):
        lst = []
        for i in self._items:
            if GetItemTypeId(i) == itemtype:
                lst.append(i)
        return lst

    def remove(self,index):
        UnitRemoveItemFromSlot(self._unit,index)

class UnitWeapon:
    def __init__(self,unit,index):
        self.parent = unit
        self.index = index
        if index > 1 or index < 0:
            print("Warning: weapon index other than 0 or 1 used in UnitWeapon.")

    @property
    def damage_tuple(self):
        return (BlzGetUnitBaseDamage(self.parent, self.index),
                BlzGetUnitDiceNumber(self.parent, self.index),
                BlzGetUnitDiceSides(self.parent, self.index))
    @damage_tuple.setter
    def damage_tuple(self,tuple):
        BlzSetUnitBaseDamage(self.parent, tuple[0], self.index)
        BlzSetUnitDiceNumber(self.parent, tuple[1], self.index)
        BlzSetUnitDiceSides(self.parent, tuple[2], self.index)
    @property
    def base_damage(self):
        return BlzGetUnitBaseDamage(self.parent, self.index)
    @base_damage.setter
    def base_damage(self,dmg):
        BlzSetUnitBaseDamage(self.parent, dmg, self.index)

    @property
    def dice_number(self):
        return BlzGetUnitDiceNumber(self.parent, self.index)
    @dice_number.setter
    def dice_number(self,dn):
        BlzSetUnitDiceNumber(self.parent, dn, self.index)

    @property
    def dice_sides(self):
        return BlzGetUnitDiceSides(self.parent, self.index)
    @dice_sides.setter
    def dice_sides(self,sides):
        BlzSetUnitDiceSides(self.parent, sides, self.index)

    @property
    def cooldown(self):
        return BlzGetUnitAttackCooldown(self.parent, self.index)
    @cooldown.setter
    def cooldown(self,cd):
        BlzSetUnitAttackCooldown(self.parent, cd, self.index)

    ## implement fields

class UnitAbility:
    def __init__(self,unit,id):
        self.parent = unit
        self.id = FourCC(id) if isinstance(id,str) else id
        # self.ability = BlzGetUnitAbility(self._handle, self.id)
        # print(self.ability)

    def remove(self):
        UnitRemoveAbility(self.parent,self.id)
        return self

    def add(self):
        UnitAddAbility(self.parent,self.id)
        return self

    def start_cooldown(self):
        BlzStartUnitAbilityCooldown(self.parent, self.id, self.cooldown)
    def reset_cooldown(self):
        BlzEndUnitAbilityCooldown(self.parent, self.id)

    def hide(self,flag=True):
        BlzUnitHideAbility(self.parent, self.id, flag)
    def show(self,flag=True):
        BlzUnitHideAbility(self.parent, self.id, not flag)

    def disable(self,flag=True,hide=True):
        BlzUnitDisableAbility(self.parent,self.id,flag,hide)
    def enable(self,flag=True,hide=False):
        BlzUnitDisableAbility(self.parent,self.id,not flag,hide)

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
    # abil = unitinstance.ability('A001')
    # abil.level = 3
    # abil.cooldown = 2.5
    def ability(self,id):
        return UnitAbility(self._handle,id)

    def weapon(self,index):
        return UnitWeapon(self._handle,index)

    @property
    def items(self):
        return UnitInventory(self._handle)

    # order functions
    def order(self, o, *args):
        if len(args) == 0:
            IssueImmediateOrder(self._handle, o)
        elif len(args) == 1:
            IssueTargetOrder(self._handle, o, args[0])
        elif len(args) == 2:
            IssuePointOrder(self._handle, o, args[0], args[1])

    def use_item(self, i, *args):
        if len(args) == 0:
            UnitUseItem(self._handle, i)
        elif len(args) == 1:
            UnitUseItemTarget(self._handle, i, args[0])
        elif len(args) == 2:
            UnitUseItemPoint(self._handle, i, args[0], args[1])

    def drop_item(self, i, *args):
        if len(args) == 1:
            UnitDropItemTarget(self._handle, i, args[0])
        elif len(args) == 2:
            UnitDropItemPoint(self._handle,i,args[0],args[1])



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
    def show(self):
        ShowUnit(self._handle,True)
    def hide(self):
        ShowUnit(self._handle,False)

    def kill(self):
        KillUnit(self._handle)

    def player_color(self,playerid):
        SetUnitColor(self._handle,ConvertPlayerColor(playerid))

    def color(self, r, g, b, a=255):
        SetUnitVertexColor(self._handle, r, g, b, a)

    def team_glow(self,show):
        BlzShowUnitTeamGlow(self._handle,show)

    def pathing(self,flag):
        SetUnitPathing(self._handle,flag)

    def blend_time(self,blendtime):
        SetUnitBlendTime(self._handle,blendtime)

    def use_food(self,usefood):
        SetUnitUseFood(self._handle,usefood)

    def is_visible_for_player(self,playerid):
        return IsUnitVisible(self._handle,Player(playerid))

    def is_type(self, type):
        return IsUnitType(self._handle, type)

    def is_race(self, race):
        return IsUnitRace(self._handle,race)

    def is_allied(self, playerid):
        return IsUnitAlly(self._handle, Player(playerid))

    def is_enemy(self, playerid):
        return IsUnitEnemy(self._handle, Player(playerid))

    def is_invisible_to_player(self, playerid):
        return IsUnitInvisible(self._handle, Player(playerid))

    def is_illusion(self):
        return IsUnitIllusion(self._handle)
    
    def is_hidden(self):
        IsUnitHidden(self._handle)
    
    def is_in_transport(self,transport):
        return IsUnitInTransport(self._handle,transport)

    def is_loaded(self):
        IsUnitLoaded(self._handle)

    def is_selectable(self):
        BlzIsUnitSelectable(self._handle)

    def animate(self,animation,rarity=None):
        if isinstance(animation,str):
            if rarity != None:
                SetUnitAnimationWithRarity(self._handle, animation, rarity)
            else:
                SetUnitAnimation(self._handle, animation)
        elif isinstance(animation, int):
            SetUnitAnimationByIndex(self._handle, animation)

    def queue_animation(self,animation):
        QueueUnitAnimation(self._handle,animation)

    def add_animation_properties(self,properties,add=True):
        AddUnitAnimationProperties(self._handle, properties, add)
    def remove_animation_properties(self,properties,remove=True):
        AddUnitAnimationProperties(self._handle, properties, not remove)

    def rescuable(self, byWhichPlayer, flag=True, range=0.0):
        SetUnitRescuable(self._handle, byWhichPlayer, flag)
        if range > 0:
            SetUnitRescueRange(self._handle,range)
    # triggering
    @staticmethod
    def _make_events():
        PlayerUnitEvent(EVENT_PLAYER_UNIT_DEATH, "on_death", Unit.get_dying)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_ATTACKED, "on_attacked", Unit.get_trigger, Unit.get_attacker)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_DAMAGED, "on_damaged", Unit.get_trigger, Unit.get_damage_source)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_DAMAGING, "on_damaging", Unit.get_damage_source, Unit.get_trigger)
        PlayerUnitEvent([EVENT_PLAYER_UNIT_ISSUED_ORDER, EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER], "on_ordered", Unit.get_ordered)
        PlayerUnitEvent(EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER, "on_ordered", Unit.get_ordered, Unit.get_order_target)

    # manual properties

    # BE CAREFUL: ASYNCHRONOUS
    @property
    def select(self):
        return IsUnitSelected(self._handle,GetLocalPlayer())
    @select.setter
    def select(self,flag):
        SelectUnit(self._handle,flag)
    # END OF ASYNCHRONOUS

    @property
    def invulnerable(self):
        return BlzIsUnitInvulnerable(self._handle)
    @invulnerable.setter
    def invulnerable(self,flag):
        SetUnitInvulnerable(self._handle,flag)

    @property
    def food_made(self):
        return GetUnitFoodMade(self._handle)
    
    @property
    def life(self):
        return GetWidgetLife(self._handle)

    @life.setter
    def life(self,hp):
        SetWidgetLife(self._handle, hp)

    @property
    def mana(self):
        return GetUnitState(self._handle, UNIT_STATE_MANA)

    @mana.setter
    def mana(self,newmana):
        SetUnitState(self._handle, UNIT_STATE_MANA, newmana)

    @property
    def food_used(self):
        return GetUnitFoodUsed(self._handle)

    @property
    def race(self):
        return GetUnitRace(self._handle)

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
        BlzSetUnitFacingEx(self._handle, newface)

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

    def look_along(self,x,y,z,bone="bone_chest"):
        SetUnitLookAt(self._handle,bone,self._handle,x*100,y*100,z*100)

    def reset_look(self):
        ResetUnitLookAt(self._handle)

    # get unit functions
    @staticmethod
    def get_attacker():
        return Handle.get(GetAttacker()) or Unit(GetAttacker)

    @staticmethod
    def get_rescuer():
        return Handle.get(GetRescuer()) or Unit(GetRescuer)

    @staticmethod
    def get_damage_source():
        return Handle.get(GetEventDamageSource()) or Unit(GetEventDamageSource)


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

AddScriptHook(Unit._make_events, MAIN_BEFORE)