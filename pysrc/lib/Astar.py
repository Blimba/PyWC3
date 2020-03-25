from .grid import *
from .cyclist import *
from ..std.effect import *
from ..std.compatibility import *
class Astar_Node(Grid2.Node,Cyclist):
    def __init__(self,grid,x,y,X,Y,z = 20):

        Grid2.Node.__init__(self,grid,x,y,X,Y)
        Cyclist.__init__(self)
        self.z = z
        self.fx = r"UI\\Feedback\\Selectioncircle\\selectioncircle.mdl"
        self.open = grid.is_pathableXY(X,Y)
        self.parent = None
        self.f = -1
        self.g = -1
        self.done = False


    def visit(self,from_node,g):
        self.fx = r"UI\\Feedback\\WaypointFlags\\UndeadWaypointFlag.mdl"
        if(self.parent == None or g < self.g):
            self.parent = from_node
            from_node.following = self
            self.g = g
            return True
        return False
    @property
    def fx(self):
        return self._fx
    @fx.setter
    def fx(self,path):
        if self._fx != None:
            self._fx.set_position(0,0,-1000)
            self._fx.destroy()
        self._fx = Effect(self.x+self.grid.grid_interval/2, self.y+self.grid.grid_interval/2, self.z, path)
        self._fx.scale = 0.5
    def destroy(self):
        Grid2.Node.destroy()
        self._fx.destroy()
        self._fx = None

    def get_neighbours(self):
        neighbours = [self.up(), self.right(), self.down(), self.left()]
        if neighbours[0] and neighbours[1] and neighbours[0].open and neighbours[1].open:
            neighbours.append(neighbours[0].right())
        if neighbours[1] and neighbours[2] and neighbours[1].open and neighbours[2].open:
            neighbours.append(neighbours[1].down())
        if neighbours[2] and neighbours[3] and neighbours[2].open and neighbours[3].open:
            neighbours.append(neighbours[2].left())
        if neighbours[3] and neighbours[0] and neighbours[3].open and neighbours[0].open:
            neighbours.append(neighbours[3].up())
        return neighbours
class Astar_Grid(Grid2):
    def heuristic(self,node,goal):
        dX = goal.X-node.X
        dY = goal.Y-node.Y
        # return abs(dX)+abs(dY)
        return math.sqrt(dX*dX+dY*dY)
    def is_pathable(self,x,y):
        return not IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY)
    def is_pathableXY(self,X,Y):
        x,y = self.XY2xy(X,Y)
        return self.is_pathable(x+self.grid_interval/2,y+self.grid_interval/2)
    def find_path(self,current, goal):
        self.goal = goal
        start = current
        start.f = self.heuristic(current,goal)
        start.g = 0
        start.fx = r"UI\\Feedback\\WaypointFlags\\NightElfWaypointFlag.mdl"
        goal.fx = r"UI\\Feedback\\WaypointFlags\\NightElfWaypointFlag.mdl"
        sorter = None
        while(current != None):
            current.open = False
            current.fx = r"UI\\Feedback\\WaypointFlags\\WaypointFlag.mdl"
            current.neighbours = current.get_neighbours()
            while True:
                if (current == goal): break
                if(len(current.neighbours) < 1 or current.done):
                    current.done = True
                    break
                neighbour = current.neighbours.pop()
                if(neighbour != None and neighbour.open and neighbour.visit(current, current.g + self.heuristic(current,neighbour))):
                    if neighbour.f < 0: neighbour.f = neighbour.g + self.heuristic(neighbour,goal)
                    sorter = current
                    while(neighbour.f > sorter.f):
                        sorter = sorter.next
                        if(sorter == current): break
                    while (sorter != current and neighbour.f == sorter.f and neighbour.g <= sorter.g):
                        sorter = sorter.next
                    sorter.prev = neighbour
                    if neighbour.f <= current.f:
                        current = neighbour
                        # if not hasattr(current,"neighbours"):
                        current.neighbours = current.get_neighbours()
                        if (current == goal): break
            if (current == goal): break
            current = current.next
            current.prev.exclude()
            if(current.next == current): break
        self.path = current
        return current
from itimer import *
class Astar:
    @staticmethod
    def find_path(from_point,to_point,pathability_function=None):
        extra = 16
        grid = 32
        fX = math.floor(from_point.x / grid)
        fY = math.floor(from_point.y / grid)
        tX = math.floor(to_point.x / grid)
        tY = math.floor(to_point.y / grid)
        ox = math.min(fX,tX)-extra/2
        oy = math.min(fY,tY)-extra/2
        g = Astar_Grid(grid, abs(fX-tX)+extra, abs(fY-tY)+extra)
        if pathability_function != None:
            g.is_pathable = pathability_function
        g.init_nodes(Vector2(ox*grid,oy*grid, True), Astar_Node)
        start = g.get_node(from_point.x,from_point.y)
        goal = g.get_node(to_point.x,to_point.y)
        best = g.find_path(start,goal)
        while (best != None and best.parent != None):
            best.fx = r"UI\\Feedback\\WaypointFlags\\OrcWaypointFlag.mdl"
            best = best.parent
        ITimer.start(0,Astar_Grid.destroy,g)
