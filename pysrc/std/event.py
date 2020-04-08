"""

Event class: a superclass to generate trigger based events in a simple manner

    Usage:

    extend by your class:

    class WhateverEvent(Event):
        def __init__(self,callback,*args):
            Event.__init__(self,callback,*args)

    This sets up the triggers and callback functions, but we need to supply it with an actual event. This is done with
    the register function:

            self.register(WhateverRegisterFunc,WhateverItNeeds)

    Here, we have to pass the blizzard native function for the TriggerRegisterFunction, and its arguments. For example:

            self.register(TriggerRegisterPlayerEvent, Player(0), EVENT_PLAYER_END_CINEMATIC)

    Now, our event will run for the callback whenever Player 0 (red) presses escape. Usage of our actual event is then
    simple:

    def mycallback():
        print('Player 0 pressed escape')
    WhateverEvent(mycallback)

ClassEvent class: a superclass to generate trigger based events on instances of classes

    An example is in the Unit class. This has a PlayerUnitEvent class, of which a simplified version is shown below

    class PlayerUnitEvent(ClassEvent):
    def __init__(self, playerunitevent, methodname, getter, *args):
        ClassEvent.__init__(self, methodname, getter,*args)
        self.register(TriggerRegisterPlayerUnitEvent, Player(playerid), playerunitevent)

    In the init of the Unit class, we then have various events generated, for example:

        PlayerUnitEvent(EVENT_PLAYER_UNIT_DEATH, "on_death", Unit.get_dying)

    Here, we tell the event manager the NAME of the method (not the actual method!), and which is the function to use
    to get the 'TriggeringUnit'. For a death event, we use Unit.get_dying(). So, now we have an event, but it doesn't
    run yet. We must now create units that actually have the methods!

    To create unit based events, we require the "on_death" function on the Unit instance. This can be done in two ways:

    u = Unit(0, b'hfoo', 0, 0)  # create a footman for player 0 at x: 0, y: 0.
    u.on_death = lambda u: print(u.name + ' has died...')

    Here, we add the on_death event for a single unit. But, we can also expand the class:

    class Footman(Unit):
        def on_death(self):
            print('a footman named {} has died'.format(self.name))

    This event will run whenever a footman that is created through Footman() dies.

"""
from .handle import *
from ..df.commonj import *
from .compatibility import *


class Event(Handle):
    def _execute_event(self):
        try:
            if self.args != None:
                self.callback(*self.args)
            else:
                self.callback()
        except:
            print(Error)
    @staticmethod
    def _triggered():
        self = Handle.get(GetTriggeringTrigger())
        if self.active:
            self._execute_event()

    def __init__(self,callback,*args):
        Handle.__init__(self,CreateTrigger())
        TriggerAddAction(self._handle, Event._triggered)
        self.callback = callback
        self.args = args
        self.active = True

    def register(self,func,*args):
        func(self._handle,*args)

class ClassEvent(Handle):
    def _execute_event(self):
        nargs = []
        for arg in self.args:
            if callable(arg):
                try:
                    nargs.append(arg())
                except:
                    nargs.append(arg)
        obj = self.getter
        try:
            obj = self.getter()
        except:
            pass
        if hasattr(obj, self.callbackname):
            try: getattr(obj, self.callbackname)(obj, *nargs)
            except: print(Error)
    @staticmethod
    def _triggered():
        self = Handle.get(GetTriggeringTrigger())
        if self.active:
            self._execute_event()


    def __init__(self,methodname,getter,*args):
        Handle.__init__(self,CreateTrigger())
        TriggerAddAction(self._handle, ClassEvent._triggered)
        self.args = args
        self.getter = getter
        self.callbackname = methodname
        self.active = True

    def register(self,func,*args):
        func(self._handle,*args)