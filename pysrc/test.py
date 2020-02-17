from std.index import *
from std.timer import Timer
from std.effect import Effect
from df.test import *

fx = None
def rotate():
    fx.lookAt(GetUnitX(gg_unit_hpea_0000),GetUnitY(gg_unit_hpea_0000),BlzGetUnitZ(gg_unit_hpea_0000))
    Timer.getExpired().restart()
def test():
    # print('a')
    fx = Effect(0,0,128,r"Abilities\\Weapons\\CannonTowerMissile\\CannonTowerMissile.mdl")

    t = Timer()
    t.start(0.01,rotate)


AddScriptHook(test,MAIN_AFTER)
