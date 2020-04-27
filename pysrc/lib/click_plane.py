from .math3d import *
from .math2d import *
from .camera import *
from .cyclist import *
from ..df.commonj import *
from ..df.blizzardj import bj_MAX_PLAYERS
from .mouseevent import MouseEvent


class ClickPlane(Rectangle, Cyclist):
    tr = None
    _node1 = None
    ignore_next = False
    _loc = None
    def __gc__(self):
        print("collecting clickplane")
    def __init__(self, minx, miny, maxx, maxy, z):
        Rectangle.__init__(self, minx, miny, maxx, maxy)
        Cyclist.__init__(self)
        self.z = z
        # make a sorted list
        if ClickPlane._node1 == None:
            ClickPlane._node1 = self
        else:
            node = ClickPlane._node1
            while z < node.z:
                node = node.next
                if(node == ClickPlane._node1): break
            node.prev = self
            if(z > ClickPlane._node1.z): ClickPlane._node1 = self

    def destroy(self):
        if self == ClickPlane._node1:
            ClickPlane._node1 = self.next
        self.exclude()
        if self == ClickPlane._node1:
            ClickPlane._node1 = None

    def set_coordinates(self,minx,miny,maxx,maxy,z):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        self.z = z

        # We need to keep the list sorted. Check if we're changing the coordinates below another:
        node = self.next
        while z < node.z:
            if self == ClickPlane._node1: ClickPlane._node1 = node
            node = node.next
            node.swap_prev()
            if node == ClickPlane._node1: break

        # Check if we're increasing our coordinates above another
        if ClickPlane._node1 != self:
            node = self.prev
            while z > node.z:
                nnode = node.prev
                node.swap_next()
                if node == ClickPlane._node1:
                    ClickPlane._node1 = self
                    break
                node = nnode

    @staticmethod
    def print_list():
        node = ClickPlane._node1
        i = 0
        lst = []
        while node != None:
            lst.append("{}:({}<{}>{})".format(str(node.z),node.prev.name,node.name,node.next.name))
            node = node.next
            i+=1
            if (node == ClickPlane._node1) or node == None or i > 5: break
        print(", ".join(lst))

    def __contains__(self, p):
        if isinstance(p, Vector2):
            return p.x >= self.minx and p.x <= self.maxx and p.y >= self.miny and p.y <= self.maxy

    def obscured(self, clickpoint, eye):
        if(self.z < clickpoint.z or self.z > eye.z):
            return None
        dx = clickpoint.x - eye.x
        dy = clickpoint.y - eye.y
        dz = eye.z - clickpoint.z
        zrat = 1-(self.z-clickpoint.z)/dz
        x = eye.x + dx * zrat
        y = eye.y + dy * zrat
        if x >= self.minx and x <= self.maxx and y >= self.miny and y <= self.maxy:
            return Vector3(x,y,self.z,True)
        return None


    @staticmethod
    def _cam_sync(ns, clickpoint, unit, order_id):
        eye = Vector3(ns.data[0],ns.data[1],ns.data[2],True)
        try:
            node = ClickPlane._node1
            while node != None:
                v = node.obscured(clickpoint, eye)
                if v != None:

                    clickpoint.update_vector(v)
                    break
                node = node.next
                if node == ClickPlane._node1: break
            IssuePointOrderById(unit, order_id, clickpoint.x, clickpoint.y)
            str = "confirmation.mdl"
            if GetOwningPlayer(unit) != GetLocalPlayer(): str = ""
            fx = AddSpecialEffect(str,clickpoint.x,clickpoint.y)
            BlzSetSpecialEffectZ(fx,clickpoint.z)
            if order_id == 851971 or order_id == 851986 or order_id == 851990:  # smart, move, patrol
                BlzSetSpecialEffectColor(fx, 0, 255, 0)
            elif order_id == 851983:  # attack
                BlzSetSpecialEffectColor(fx, 255, 0, 0)
            else:  # spells and stuff?
                BlzSetSpecialEffectColor(fx, 0, 0, 255)
            DestroyEffect(fx)
        except: print(Error)
        clickpoint.destroy()

    @staticmethod
    def _ordered(e):
        if e.unit_order != None:
            MoveLocation(ClickPlane._loc,e.x,e.y)
            clickpoint = Vector3(e.x, e.y, GetLocationZ(ClickPlane._loc))
            try: Camera.sync_eye_position(GetPlayerId(GetOwningPlayer(e.ordered_unit)),ClickPlane._cam_sync, clickpoint, e.ordered_unit, e.unit_order)
            except: print(Error)
            IssueImmediateOrder(e.ordered_unit, "stop")

    @staticmethod
    def _init():
        MouseEvent(ClickPlane._ordered)
        ClickPlane._loc = Location(0,0)


AddScriptHook(ClickPlane._init, MAIN_BEFORE)
