"""

Scene system to make delicate timing easier. Be careful: runtime errors within it will not automatically display!

"""
from ..std.index import *
from .itimer import *

class Scene(CTimer):
    def __init__(self,func):
        self.func = func
        self.t = None
        self.started = False

    def resume(self):
        if self.t != None and self.t.get_remaining() > 0:
            print('resume scene',self.t.get_remaining(),self.t.get_elapsed())
            ITimer.recycle.append(self.t)
            self.t = self.timer(self.t.get_remaining(),self.resume)
        else:
            coroutine.resume(self.co,self)

    def pause(self):
        coroutine.pause()

    def wait(self,duration):
        self.time += duration
        self.t = self.timer(duration, self.resume)
        coroutine.pause()

    def stop(self):
        if self.t != None:
            self.t.pause()

    def destroy(self):
        if self.t != None:
            self.t.pause()
            ITimer.recycle.append(self.t)

    def wait_until(self,time):
        self.t = self.timer(time-self.t, self.resume)
        self.time = time
        coroutine.pause()

    def start(self,*args):
        self.started = True
        self.co = coroutine.create(self.func)
        self.time = 0
        coroutine.resume(self.co,self,*args)


    def cinematic_mode(self,boolean):
        if boolean:
            # ClearTextMessages()
            ShowInterface(False, 0.5)
            EnableUserControl(False)
            EnableOcclusion(False)
        else:
            ShowInterface(True, 0.5)
            EnableUserControl(True)
            EnableOcclusion(True)

    def fade_out(self,duration):
        self.fade(duration,[0,0,0,255],[0,0,0,0])

    def fade_in(self,duration):
        self.fade(duration,[0,0,0,0],[0,0,0,255])

    def fade(self,duration,rgba1,rgba2,bmode = None,tex = None):
        if bmode == None:
            bmode = BLEND_MODE_BLEND
        if tex == None:
            tex = r"ReplaceableTextures\\CameraMasks\\White_mask.blp"
        SetCineFilterTexture(tex)
        SetCineFilterBlendMode(bmode)
        SetCineFilterTexMapFlags(TEXMAP_FLAG_NONE)
        SetCineFilterStartUV(0, 0, 1, 1)
        SetCineFilterEndUV(0, 0, 1, 1)
        SetCineFilterStartColor(*rgba1)
        SetCineFilterEndColor(*rgba2)
        SetCineFilterDuration(duration)
        DisplayCineFilter(True)