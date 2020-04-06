from ..std.index import *
from .itimer import *

class Scene:
    def __init__(self,func):
        self.func = func

    def resume(t,self):
        try: coroutine.resume(self.co,self)
        except: print(Error)

    def pause(self):
        coroutine.pause()

    def wait(self,duration):
        self.t += duration
        ITimer.start(duration,Scene.resume,self)
        coroutine.pause()

    def wait_until(self,time):
        ITimer.start(time-self.t, Scene.resume, self)
        self.t = time
        coroutine.pause()

    def start(self):
        try:
            self.co = coroutine.create(self.func)
        except:
            print(Error)
        self.t = 0
        coroutine.resume(self.co,self)


    def cinematic_mode(self,boolean):
        if boolean:
            ClearTextMessages()
            ShowInterface(False, 0.5)
            EnableUserControl(False)
            EnableOcclusion(False)
        else:
            ShowInterface(True, 0.5)
            EnableUserControl(True)
            EnableOcclusion(True)


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