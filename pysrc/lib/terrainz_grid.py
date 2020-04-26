from ..std.index import *
from .math3d import *
from .math2d import *
from ..df.blizzardj import bj_mapInitialPlayableArea

class TerrainGrid(Rectangle):
    grids = []
    _loc = None
    def __init__(self,r,sampling=8):
        Rectangle.__init__(self,GetRectMinX(r),GetRectMinY(r),GetRectMaxX(r),GetRectMaxY(r))
        TerrainGrid.grids.append(self)
        self.sampling = sampling
        _l = TerrainGrid._loc
        _zgrid=None
        """[[luacode]]
        local _zgrid = {}
        """
        for X in range(math.floor(self.maxx - self.minx) / sampling):
            """[[luacode]]
            _zgrid[X] = {}
            """
            for Y in range(math.floor(self.maxy - self.miny) / sampling):
                MoveLocation(_l, X * sampling + self.minx, Y * sampling + self.miny)
                """[[luacode]]
                _zgrid[X][Y] = GetLocationZ(_l)
                """
        self.grid = _zgrid

    def get_z(self,x,y):
        X = math.floor((x - self.minx) / self.sampling)
        Y = math.floor((y - self.miny) / self.sampling)
        return self.grid[X][Y]

    @staticmethod
    def z(x,y):
        for g in TerrainGrid.grids:
            if Vector2(x,y,True) in g:
                return g.get_z(x,y)
        MoveLocation(TerrainGrid._loc,x,y)
        return GetLocationZ(TerrainGrid._loc)
    @staticmethod
    def _init():
        TerrainGrid._loc = Location(0,0)
AddScriptHook(TerrainGrid._init,MAIN_BEFORE)

def _ft(x,y,temp=False):
    z = TerrainGrid.z(x,y)
    if IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY): z += 2000.0
    return Vector3(x,y,z,temp)
Vector3.from_terrain = _ft

