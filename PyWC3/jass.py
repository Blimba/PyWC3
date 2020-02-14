import re
from config import *
class Jass:
    @staticmethod
    def convertCommonJ():
        inf = os.path.join(JASS_FOLDER,'common.j')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())

        funcs = re.findall("^\s*(constant)?\s*native\s+([^\s]+)\s+takes\s+(.+)\s+returns\s+(.+)$",lns,flags=re.MULTILINE)
        consts = re.findall("^\s*(constant)?\s*([^\s]+)\s+([^\s]+)\s+=\s+(.+?)(\/\/.*?)?$",lns,flags=re.MULTILINE)

        outf = os.path.join(PYTHON_SOURCE_FOLDER,'obj','commonj.py')
        with open(outf, "w") as f:
            f.write("# -- DO NOT INCLUDE --\n")

            for match in funcs:
                if match[2] != "nothing":
                    vars = match[2].split(",")
                    names = [var.split(" ")[-1] for var in vars]
                else:
                    names = []
                f.write("{} = lambda {}: None\n".format(match[1],", ".join(names)))
            for match in consts:
                rs = re.sub("(\$[A-Z0-9]+)",lambda obj: str(int("0x{}".format(obj.group(0)[1:]),16)),match[3])
                f.write("{} = {}\n".format(match[2],rs.replace("false","False").replace("true","True")))
        print("Saved to {}.".format(outf))

    @staticmethod
    def convertBlizzardJ():
        inf = os.path.join(JASS_FOLDER,'blizzard.j')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())
        outf = os.path.join(PYTHON_SOURCE_FOLDER,'obj','blizzardj.py')
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
        inf = os.path.join(JASS_FOLDER,'common.ai')
        print("Converting {}...".format(inf))
        with open(inf, "r") as f:
            lns = "".join(f.readlines())
        outf = os.path.join(PYTHON_SOURCE_FOLDER,'obj','commonai.py')
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
    def convertAll():
        Jass.convertCommonJ()
        Jass.convertCommonAI()
        Jass.convertBlizzardJ()


