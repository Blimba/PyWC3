from .math3d import *
from .math2d import *
from .camera import *
from .cyclist import *
from ..df.commonj import *
from ..df.blizzardj import bj_MAX_PLAYERS



class ClickPlane(Rectangle, Cyclist):
    tr = None
    _node1 = None
    ignore_next = False
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

    def __contains__(self, p):
        if isinstance(p, Vector2):
            return p.x >= self.minx and p.x <= self.maxx and p.y >= self.miny and p.y <= self.maxy

    def obscured(self, clickpoint, camera):
        if(self.z < clickpoint.z or self.z > camera.source.z):
            return False
        dx = clickpoint.x - camera.source.x
        dy = clickpoint.y - camera.source.y
        dz = camera.source.z - clickpoint.z
        zrat = 1-(self.z-clickpoint.z)/dz
        x = camera.source.x + dx * zrat
        y = camera.source.y + dy * zrat
        self.redirect = Vector2(x,y)
        if self.redirect in self:  # if the point is within the bounds
            self.redirect = Vector3(x,y,self.z,True)
            return True
        return False

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

    def destroy(self):
        if self == ClickPlane._node1:
            ClickPlane._node1 = self.next
        self.exclude()
        if self == ClickPlane._node1:
            ClickPlane._node1 = None

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



    @staticmethod
    def _cam_sync(camera, clickpoint, unit, order_id):
        try:
            node = ClickPlane._node1
            while True:
                if node.obscured(clickpoint, camera):
                    # ClickPlane.ignore_next = True
                    IssuePointOrderById(unit, order_id, node.redirect.x, node.redirect.y)
                    clickpoint.x = node.redirect.x
                    clickpoint.y = node.redirect.y
                    clickpoint.z = node.redirect.z
                    break
                node = node.next
                if node == ClickPlane._node1: break
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
    def _ordered():
        if ClickPlane.ignore_next:
            ClickPlane.ignore_next = False
            return False
        clickpoint = Vector3.from_terrain(GetOrderPointX(), GetOrderPointY())
        try: Camera().sync_from_player(GetOwningPlayer(GetOrderedUnit()), ClickPlane._cam_sync, clickpoint, GetOrderedUnit(), GetIssuedOrderId())
        except: print(Error)

    @staticmethod
    def _init():
        ClickPlane.tr = CreateTrigger()
        for i in range(bj_MAX_PLAYERS):
            TriggerRegisterPlayerUnitEvent(ClickPlane.tr, Player(i), EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER, None)
        TriggerAddAction(ClickPlane.tr, ClickPlane._ordered)

AddScriptHook(ClickPlane._init, MAIN_BEFORE)

# overwrite natives, as trigger orders should be ignored
_IssuePointOrderById = IssuePointOrderById
def IssuePointOrderById(whichUnit, order, x, y):
    ClickPlane.ignore_next = True
    _IssuePointOrderById(whichUnit, order, x, y)

_IssuePointOrder = IssuePointOrder
def IssuePointOrder(whichUnit, order, x, y):
    ClickPlane.ignore_next = True
    _IssuePointOrder(whichUnit, order, x, y)