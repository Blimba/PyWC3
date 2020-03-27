from .compatibility import *

MAIN_BEFORE = "main::before"
MAIN_AFTER = "main::after"
CONFIG_BEFORE = "config::before"
CONFIG_AFTER = "config::after"
MAP_LOAD = "map::load"
hooks = {
    MAIN_BEFORE: [],
    MAIN_AFTER: [],
    CONFIG_BEFORE: [],
    CONFIG_AFTER: [],
    MAP_LOAD: []
}

oldMain = main
oldConfig = config


def newmain():
    def timeout():
        for func in hooks[MAP_LOAD]:
            try: func()
            except: print(Error)
    for func in hooks[MAIN_BEFORE]:
        try: func()
        except: print(Error)
    oldMain()
    for func in hooks[MAIN_AFTER]:
        try: func()
        except: print(Error)
    TimerStart(CreateTimer(),0.0,False,timeout)

def newconfig():
    for func in hooks[CONFIG_BEFORE]:
        try: func()
        except: print(Error)
    oldConfig()
    for func in hooks[CONFIG_AFTER]:
        try: func()
        except: print(Error)


main = newmain
config = newconfig
def AddScriptHook(func, place = MAIN_AFTER):
    if place in hooks:
        hooks[place].append(func)
