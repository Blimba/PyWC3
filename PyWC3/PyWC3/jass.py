import json
import os
import re

try:
    with open("config.json", "r") as f:
        cfg = json.load(f)
except:
    raise Exception("Configuration file config.json not found in location: {}".format(os.getcwd()))
class Jass:
    @staticmethod
    def convertCommonJ():
        inf = os.path.join(cfg['JASS_FOLDER'],'common.j')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())

        funcs = re.findall("^\s*(constant)?\s*native\s+([^\s]+)\s+takes\s+(.+)\s+returns\s+(.+)$",lns,flags=re.MULTILINE)
        consts = re.findall("^\s*(constant)?\s*([^\s]+)\s+([^\s]+)\s+=\s+(.+?)(\/\/.*?)?$",lns,flags=re.MULTILINE)

        outf = os.path.join(cfg['PYTHON_SOURCE_FOLDER'],cfg['DEF_SUBFOLDER'],'commonj.py')
        with open(outf, "w") as f:
            f.write("# -- DO NOT INCLUDE --\n")
            for match in funcs:
                if match[0] == 'constant' or match[0] == '':
                    match = [m for m in match[1:]]
                if match[1] != "nothing":
                    vars = match[1].split(",")
                    names = [var.split(" ")[-1] for var in vars]
                else:
                    names = []
                f.write("{} = lambda {}: None\n".format(match[0],", ".join(names)))
            for match in consts:
                if match[0] == 'constant' or match[0] == '':
                    match = [m for m in match[1:]]
                rs = re.sub("(\$[A-Z0-9]+)",lambda obj: str(int("0x{}".format(obj.group(0)[1:]),16)),match[2])
                f.write("{} = {}\n".format(match[1],rs.replace("false","False").replace("true","True")))
        print("Saved to {}.".format(outf))

    @staticmethod
    def convertBlizzardJ():
        inf = os.path.join(cfg['JASS_FOLDER'],'blizzard.j')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())
        outf = os.path.join(cfg['PYTHON_SOURCE_FOLDER'],cfg['DEF_SUBFOLDER'],'blizzardj.py')
        with open(outf, "w") as f:
            f.write("# -- DO NOT INCLUDE --\nfrom .commonj import *\n")
            nofuncs = re.sub("^\s*function([\S\s]+)endfunction.*$","",lns,flags = re.MULTILINE)
            consts = re.findall("^\s*(constant\s*)?([^\s]+)\s+([^\s]+)\s+=\s+(.+?)(\/\/.*?)?$", nofuncs, flags=re.MULTILINE)
            for match in consts:
                f.write("{} = {}\n".format(match[2],match[3].replace("null","None").replace("false", "False").replace("true", "True")))
            funcs = re.findall("^\s*function\s+([^\s]+)\s+takes\s+(.+)\s+returns\s+(.+)$",lns,flags=re.MULTILINE)
            for match in funcs:
                if match[1] != "nothing":
                    vars = match[1].split(",")
                    names = [var.split(" ")[-1] for var in vars]
                else:
                    names = []
                f.write("{} = lambda {}: None\n".format(match[0],", ".join(names)))
        print("Saved to {}.".format(outf))

    @staticmethod
    def convertCommonAI():
        inf = os.path.join(cfg['JASS_FOLDER'],'common.ai')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())
        outf = os.path.join(cfg['PYTHON_SOURCE_FOLDER'],cfg['DEF_SUBFOLDER'],'commonai.py')
        with open(outf, "w") as f:
            f.write("# -- DO NOT INCLUDE --\nfrom .commonj import *\n")
            nofuncs = re.sub("^\s*function([\S\s]+)endfunction.*$","",lns,flags = re.MULTILINE)
            consts = re.findall("^\s*(constant\s*)?([^\s]+)\s+([^\s]+)\s+=\s+(.+?)(\/\/.*?)?$", nofuncs, flags=re.MULTILINE)
            for match in consts:
                f.write("{} = {}\n".format(match[2],match[3].replace("null","None").replace("false", "False").replace("true", "True")))
            funcs = re.findall("^\s*function\s+([^\s]+)\s+takes\s+(.+)\s+returns\s+(.+)$",lns,flags=re.MULTILINE)
            for match in funcs:
                if match[1] != "nothing":
                    vars = match[1].split(",")
                    names = [var.split(" ")[-1] for var in vars]
                else:
                    names = []
                f.write("{} = lambda {}: None\n".format(match[0],", ".join(names)))
            funcs = re.findall("^\s*(constant)?\s*native\s+([^\s]+)\s+takes\s+(.+)\s+returns\s+(.+)$", lns, flags=re.MULTILINE)
            for match in funcs:
                takes = match[2].strip()
                if takes != "nothing":
                    vars = takes.split(",")
                    names = [var.split(" ")[-1] for var in vars]
                else:
                    names = []
                f.write("{} = lambda {}: None\n".format(match[1],", ".join(names)))
        print("Saved to {}.".format(outf))

    @staticmethod
    def convert_all():
        Jass.convertCommonJ()
        Jass.convertCommonAI()
        Jass.convertBlizzardJ()


