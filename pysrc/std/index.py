from .compatibility import *
from .handle import *

MAIN_BEFORE = "main::before"
MAIN_AFTER = "main::after"
CONFIG_BEFORE = "config::before"
CONFIG_AFTER = "config::after"

hooks = {
    MAIN_BEFORE: [],
    MAIN_AFTER: [],
    CONFIG_BEFORE: [],
    CONFIG_AFTER: [],
}

oldMain = main
oldConfig = config
def newmain():
    for func in hooks[MAIN_BEFORE]: func()
    oldMain()
    for func in hooks[MAIN_AFTER]: func()

def newconfig():
    for func in hooks[CONFIG_BEFORE]: func()
    oldConfig()
    for func in hooks[CONFIG_AFTER]: func()

main = newmain
config = newconfig
def AddScriptHook(func, place = MAIN_AFTER):
    if place in hooks:
        hooks[place].append(func)
