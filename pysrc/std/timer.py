from handle import *
from ..df.commonj import *
"""

    A wrapper for the blizzard timers
    
    Usage:
    
    def timeout():
        t = Timer.get_expired()
        print(t.data)
        t.destroy()
    t = Timer()
    # do whatever you want with, such as attach things that we can use on timeout
    t.data = 5
    t.start(1.0, timeout)

"""
class TimerDialog(Handle):
    def __init__(self,t):
        Handle.__init__(self,CreateTimerDialog(t._handle))
        self.active = True
    def display(self):
        TimerDialogDisplay(self._handle,True)
        return self
    def hide(self):
        TimerDialogDisplay(self._handle, False)
        return self
    def set_time_color(self,r,g,b,a=255):
        TimerDialogSetTimeColor(self._handle,r,g,b,a)
        return self
    def set_title_color(self,r,g,b,a=255):
        TimerDialogSetTitleColor(self._handle,r,g,b,a)
        return self
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self,title):
        self._title = title
        TimerDialogSetTitle(self._handle, title)
    def destroy(self):
        self.hide()
        DestroyTimerDialog(self._handle)
        self.active = False
class Timer(Handle):
    def __init__(self,periodic=False):
        self.periodic = periodic
        Handle.__init__(self,CreateTimer())
        self._dialog = None
        self.remaining = -1

    # def __gc__(self):
    #     # currently this never runs
    #     print('timer gc',self._handle,self.get_elapsed())
    #     self.destroy()

    def start(self,time,callback):
        self.time = time
        self.callback = callback
        TimerStart(self._handle,time,self.periodic,callback)

    def restart(self):
        if self.callback:
            TimerStart(self._handle,self.time,self.periodic,self.callback)

    @staticmethod
    def get_expired():
        return Handle.get(GetExpiredTimer())

    def pause(self):
        if self.periodic:
            # this also has weird sideeffects for periodic timers, but that's how it is.
            PauseTimer(self._handle)
        else:
            # non-periodic timers behave funky when paused. https://www.hiveworkshop.com/threads/issues-with-timer-functions.309433/
            self.remaining = self.get_remaining()
            TimerStart(self._handle,0.0,False,None)
        return self

    def resume(self):
        if self.periodic:
            ResumeTimer(self._handle)
        else:
            # non-periodic timers behave funky when paused. https://www.hiveworkshop.com/threads/issues-with-timer-functions.309433/
            if self.remaining >= 0:
                TimerStart(self._handle, self.remaining, False, self.callback)
            self.remaining = -1
        return self

    def destroy(self):
        if self.dialog != None and self.dialog.active == True:
            self._dialog.destroy()
        Handle.destroy(self)
        DestroyTimer(self._handle)

    def get_elapsed(self):
        return TimerGetElapsed(self._handle)

    def get_remaining(self):
        return TimerGetRemaining(self._handle)

    @property
    def dialog(self):
        if self._dialog == None or self._dialog.active == False:
            self._dialog = TimerDialog(self)
        return self._dialog
    @dialog.setter
    def dialog(self,dialog):
        if self.dialog != None and self.dialog.active == True:
            self._dialog.destroy()
        self._dialog = dialog
