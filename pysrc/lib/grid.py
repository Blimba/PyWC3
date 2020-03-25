from math2d import *


class Grid2:
    class Node:
        reuse = []
        _fifo_buffer_size = 100  # this is the amount of temporary nodes used
        def __new__(cls,parent_grid,x,y,X,Y):
            if len(Grid2.Node.reuse) > Grid2.Node._fifo_buffer_size:
                o = Grid2.Node.reuse.pop(0)
                return o
            else:
                o = object.__new__(cls)
                return o
        def __init__(self,parent_grid,x,y,X,Y):
            self.grid = parent_grid
            self.x = x
            self.y = y
            self.X = X
            self.Y = Y
        def destroy(self):
            Grid2.Node.reuse.append(self)

        def up(self, wrap=False):
            if not wrap and self.Y+1 >= self.grid.sY: return None
            return self.grid[self.X,self.Y+1]
        def down(self, wrap=False):
            if not wrap and  self.Y <= 0: return None
            return self.grid[self.X,self.Y-1]
        def left(self, wrap=False):
            if not wrap and  self.X <= 0: return None
            return self.grid[self.X-1,self.Y]
        def right(self, wrap=False):
            if not wrap and  self.X + 1 >= self.grid.sX: return None
            return self.grid[self.X+1,self.Y]
        def __str__(self):
            return "Node[{},{}] at x: {}, y: {}".format(self.X, self.Y, self.x, self.y)

    def __init__(self,grid_interval,size_x,size_y):
        self.grid_interval = grid_interval
        self.sX = size_x
        self.sY = size_y
        self._offset = Vector2(0.0,0.0)

    def init_nodes(self,offset,node_class=None):
        node_class = node_class or Grid2.Node
        self.data = []
        self.offset = offset
        for X in range(self.sX):
            self.data.append([])
            for Y in range(self.sY):
                self.data[X].append(node_class(self,X*self.grid_interval+self._offset.x,Y*self.grid_interval+self._offset.y,X,Y))

    def destroy(self,keep_nodes = False):
        if not keep_nodes and callable(self.data[0][0].destroy):
            for X in range(self.sX):
                for Y in range(self.sY):
                    self.data[X][Y].destroy()
        self._offset.destroy()

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self,v):
        self._offset.x = v.x
        self._offset.y = v.y

    def get_node(self,x,y):
        X = math.floor((x-self._offset.x) / self.grid_interval)
        Y = math.floor((y-self._offset.y) / self.grid_interval)
        if X < 0 or Y < 0 or X >= self.sX or Y >= self.sY:
            return None
        return self.data[X][Y]

    def xy2XY(self,x,y):
        X = math.floor(x / self.grid_interval)
        Y = math.floor(y / self.grid_interval)
        if X < 0 or Y < 0 or X >= self.sX or Y >= self.sY:
            return None
        return X, Y

    def XY2xy(self,X,Y):
        return X*self.grid_interval+self._offset.x, Y*self.grid_interval+self._offset.y


    def __getitem__(self, i):
        if isinstance(i,int):
            x = math.fmod(i,self.sX)
            y = math.floor(i/self.sX)
            return self.data[x][y]
        elif isinstance(i,tuple) and len(i) == 2:
            if isinstance(i[0],int):
                return self.data[i[0]][i[1]]
            if isinstance(i[0],slice):
                lst = []
                for d in self.data[i[0]]:
                    lst.append(d[i[1]])
                return lst
        return []

