# --DO NOT INCLUDE--
"""

This script is here only for code completion reasons, to make python think it has access to the lua/wc3 functions

"""
from ..df.commonj import *
from ..df.blizzardj import *
from ..df.commonai import *

def main():
    pass
def config():
    pass

def FourCC(str):
    return 0

Error=""  # this is the Error message to use in try/except blocks
class math:
    @staticmethod
    def random():
        return 0.0

    @staticmethod
    def floor(a):
        return a

    @staticmethod
    def ceil(a):
        return a

    @staticmethod
    def min(*args):
        return 0

    @staticmethod
    def max(*args):
        return 0

    @staticmethod
    def sin(x): return 0

    @staticmethod
    def cos(x): return 0

    @staticmethod
    def tan(x): return 0

    @staticmethod
    def atan(x,y=0): return 0

    @staticmethod
    def acos(x): return 0

    @staticmethod
    def asin(x): return 0

    @staticmethod
    def sqrt(x): return 0

class coroutine:
    @staticmethod
    def resume(co,*args):
        pass

    @staticmethod
    def create(co):
        return co

    @staticmethod
    def pause(*args):
        return None

    @staticmethod
    def status(co):
        return "dead"

class os:
    @staticmethod
    def clock():
        return 0.0
    @staticmethod
    def time():
        return 0.0