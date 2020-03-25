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
    def random(self):
        return 0.0
    def floor(self,a):
        return a
    def ceil(self,a):
        return a
    def min(self,*args):
        return 0
    def max(self,*args):
        return 0

class coroutine:
    @staticmethod
    def resume(co):
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