from ..df.commonj import *
from .timer import Timer
from .index import *
from .unit import Unit
# CreateSound(filename,looping,d3d,stopwhenoutofrange,fadeinrate,fadeoutrate,eaxsetting)



class Sound:
    def __init__(self,filename,looping=False,variations=1):
        self.filename = filename
        self.t = Timer()
        self.t.data = self
        self.looping = looping
        self.variations = variations

    def stop(self):
        if self.snd != None:
            StopSound(self.snd)

    @staticmethod
    def _timeout():
        self = Timer.get_expired().data
        StartSound(self.snd)
        if not self.looping:
            KillSoundWhenDone(self.snd)
    def play_offset(self,offset=0.0,volume=1.0,pitch=1.0,playerid=-1):
        self.play(volume,pitch,playerid)
        SetSoundPlayPosition(self.snd,offset)
    def play(self,volume=1.0,pitch=1.0,playerid=-1):
        fn = self.filename
        if self.variations > 1:
            fn = fn.format(str(math.floor(math.random()*self.variations)+1))
        if self.looping:
            self.snd = CreateSound(fn, True, False, True, 10, 10, "DefaultEAXON")
        else:
            self.snd = CreateSound(fn, False, False, True, 10, 10, "DefaultEAXON")
        if volume > 1.0: volume = 1.0
        elif volume < 0.0: volume = 0.0
        if playerid < 0 or GetLocalPlayer() == Player(playerid):
            SetSoundVolume(self.snd,math.floor(volume*127))
        else:
            SetSoundVolume(self.snd, 0)
        SetSoundChannel(self.snd,5)
        SetSoundPitch(self.snd,pitch)
        self.t.start(0.0,Sound._timeout)
        return self

    @staticmethod
    def _preload():
        self = Timer.get_expired().data
        StartSound(self.snd)
        StopSound(self.snd)
    def preload(self):
        fn = self.filename
        if self.variations > 1:
            fn = fn.format(str(math.floor(math.random()*self.variations)+1))
        if self.looping:
            self.snd = CreateSound(fn, True, False, True, 10, 10, "DefaultEAXON")
        else:
            self.snd = CreateSound(fn, False, False, True, 10, 10, "DefaultEAXON")
        SetSoundVolume(self.snd, 0)
        SetSoundChannel(self.snd,5)
        SetSoundPitch(self.snd,1)
        self.t.start(0.0,Sound._preload)
        return self

class Sound3D:
    def __init__(self,filename,looping=False,variations=1):
        self.filename = filename
        self.t = Timer()
        self.t.data = self
        self.looping = looping
        self.snd = None
        self.variations = variations

    @staticmethod
    def _timeout():
        self = Timer.get_expired().data
        StartSound(self.snd)
        if not self.looping:
            KillSoundWhenDone(self.snd)

    def stop(self):
        if self.snd != None:
            StopSound(self.snd)

    def play_position(self,x,y,z,volume=1.0,pitch=1.0,playerid=-1):
        fn = self.filename
        if self.variations > 1:
            fn = fn.format(str(math.floor(math.random()*self.variations)+1))
        if self.looping:
            self.snd = CreateSound(fn, True, True, True, 10, 10, "DefaultEAXON")
        else:
            self.snd = CreateSound(fn, False, True, True, 10, 10, "DefaultEAXON")
        if volume > 1.0: volume = 1.0
        elif volume < 0.0: volume = 0.0
        if playerid < 0 or GetLocalPlayer() == Player(playerid):
            SetSoundVolume(self.snd,math.floor(volume*127))
        else:
            SetSoundVolume(self.snd, 0)
        SetSoundChannel(self.snd,5)
        SetSoundPitch(self.snd,pitch)
        SetSoundDistances(self.snd, 200., 10000.)
        SetSoundDistanceCutoff(self.snd, 6000.)
        SetSoundConeAngles(self.snd, 0., 0., 127)
        SetSoundConeOrientation(self.snd, 0., 0., 0.)
        SetSoundPosition(self.snd,x,y,z)
        self.t.start(0.0,Sound._timeout)
        return self

    def play_unit(self,unit,volume=1.0,pitch=1.0,playerid=-1):
        if self.looping:
            self.snd = CreateSound(self.filename, True, True, True, 10, 10, "DefaultEAXON")
        else:
            self.snd = CreateSound(self.filename, False, True, True, 10, 10, "DefaultEAXON")
        if volume > 1.0: volume = 1.0
        elif volume < 0.0: volume = 0.0
        if playerid < 0 or GetLocalPlayer() == Player(playerid):
            SetSoundVolume(self.snd,math.floor(volume*127))
        else:
            SetSoundVolume(self.snd, 0)
        SetSoundChannel(self.snd,5)
        SetSoundPitch(self.snd,pitch)
        SetSoundDistances(self.snd, 200., 2000.)
        SetSoundDistanceCutoff(self.snd, 1500.)
        SetSoundConeAngles(self.snd, 0., 0., 127)
        SetSoundConeOrientation(self.snd, 0., 0., 0.)
        if isinstance(unit,Unit):
            AttachSoundToUnit(self.snd, unit.handle)
        else:
            AttachSoundToUnit(self.snd, unit)
        self.t.start(0.0,Sound._timeout)
        return self

    @staticmethod
    def _preload():
        self = Timer.get_expired().data
        StartSound(self.snd)
        StopSound(self.snd)
    def preload(self):
        fn = self.filename
        if self.variations > 1:
            fn = fn.format(str(math.floor(math.random()*self.variations)+1))
        if self.looping:
            self.snd = CreateSound(fn, True, True, True, 10, 10, "DefaultEAXON")
        else:
            self.snd = CreateSound(fn, False, True, True, 10, 10, "DefaultEAXON")
        SetSoundVolume(self.snd, 0)
        SetSoundChannel(self.snd,5)
        SetSoundPitch(self.snd,1)
        SetSoundDistances(self.snd, 200., 10000.)
        SetSoundDistanceCutoff(self.snd, 6000.)
        SetSoundConeAngles(self.snd, 0., 0., 127)
        SetSoundConeOrientation(self.snd, 0., 0., 0.)
        SetSoundPosition(self.snd,0,0,0)
        self.t.start(0.0,Sound._preload)
        return self