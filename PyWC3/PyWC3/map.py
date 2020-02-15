
import os
import subprocess
import re
from pythonlua.translator import Translator
import shutil
import json

class Map:
    def __init__(self, file, **kwargs):
        with open("config.json","r") as f:
            self.cfg = json.load(f)
        if os.path.exists(os.path.join(self.cfg['MAP_FOLDER'], file)):
            self.file = file
            # make a translator object with the main and config added to the currect context so it doesn't output them as local
            self.translator = Translator(locals=['main', 'config'], show_ast=kwargs.get('show_ast',False))
        else:
            raise Exception("Mapfile {} not found!".format(os.path.join(os.getcwd(),self.cfg['MAP_FOLDER'], file)))

    def run(self):
        f = os.path.join(os.getcwd(),"{}\\{}".format(self.cfg['DIST_FOLDER'], self.file))
        if os.path.exists(f):
            print("Launching map {}".format(f))
            process = subprocess.Popen([self.cfg['WAR3_EXE'], '-launch', '-nativefullscr', '-loadfile', '{}'.format(f)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        else:
            raise Exception("Mapfile {} not found!".format(os.path.join(self.cfg['DIST_FOLDER'], self.file)))

    def edit(self):
        f = os.path.join(os.getcwd(),"{}\\{}".format(self.cfg['MAP_FOLDER'], self.file))
        if os.path.exists(f):
            print("Editing map {}".format(f))
            process = subprocess.Popen([self.cfg['WE_EXE'], '-launch', '-loadfile', '{}'.format(f)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        else:
            raise Exception("Mapfile {} not found!".format(os.path.join(self.cfg['MAP_FOLDER'], self.file)))

    def translate_file(self, file):
        print("> Translating file {}...".format(file))
        with open(file, "r") as f:
            content = "".join(f.readlines())
        content = re.sub("^import (.+)$", "", content, flags=re.MULTILINE)
        content = re.sub("^from (.+) import (.+)*", "", content, flags=re.MULTILINE)
        return self.translator.translate(
            content)  # re.sub("local (.+) = require \"(.+)\"","",self.translator.translate(content))

    def get_dependencies(self, file, exclude=True):
        print("> Reading file {}...".format(file))
        try:
            with open(file, "r") as f:
                lst = []

                content = "".join(f.readlines())
                srcdir = os.path.dirname(file)
                # exclude files containing python only code
                if re.match("^# --DO NOT INCLUDE--$", content, re.MULTILINE):
                    return []
                if not exclude:
                    lst.append(file)
                matches = re.findall("^import (.+)", content, re.MULTILINE)
                for match in matches:
                    newfile = match.replace('.', '\\').strip('\\')
                    for d in self.get_dependencies("{}.py".format(os.path.join(srcdir, newfile)), exclude=False):
                        # print("d",d)
                        lst.append(d)
                matches = re.findall("^from (.+) import", content, re.MULTILINE)
                for match in matches:
                    newfile = match.replace('.', '\\').strip('\\')
                    for d in self.get_dependencies("{}.py".format(os.path.join(srcdir, newfile)), exclude=False):
                        # print("d",d)
                        lst.append(d)
        except:
            raise Exception("Cannot find python source file {}".format(file))
        return lst

    def build(self):
        # remove extension if required
        filename = self.file
        spl = filename.split(".")
        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])

        print("> Generating distribution map files in {}...".format(os.path.join(self.cfg['DIST_FOLDER'], self.file)))
        # delete previous distribution
        try: shutil.rmtree(os.path.join(self.cfg['DIST_FOLDER'], self.file))
        except: pass  # the dist map does not exist yet, no problem!
        # copy the map
        shutil.copytree(os.path.join(self.cfg['MAP_FOLDER'], self.file),os.path.join(self.cfg['DIST_FOLDER'], self.file))
        # write translated lua files
        with open(os.path.join(self.cfg['DIST_FOLDER'], self.file, "war3map.lua"), "w") as f:
            # write map code
            with open(os.path.join(self.cfg['MAP_FOLDER'], self.file, "war3map.lua"), "r") as f2:
                f.write("-- Generated map code\n")
                f.write("".join(f2.readlines()))
                f.write("\n")
            # write lua functions for pythonlua
            print("> Writing lua header...")
            f.write(Translator.get_luainit())
            # write python required libraries
            for file in self.get_dependencies(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))):
                f.write("-- Imported module {}\n".format(file))
                f.write(self.translate_file(file))
                print("> Appended file {}.".format(file))
                f.write("\n")
            # write
            f.write("-- Main map code\n")
            f.write(self.translate_file(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))
            print("> Appended file {}.".format(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))
        print("Build completed.")
        # WRITE A CODE CHECKER WITH LUA EXECUTION HERE

    def generate_python_source(self):
        filename = self.file
        spl = filename.split(".")
        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])
        fn = os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'],"{}.py".format(filename))
        if os.path.exists(fn):
            raise Exception("Python source file {} already exists!".format(fn))
        with open(fn,"w") as f:
            print("Generating python script {}...".format(fn))
            f.write("""from std.index import *
            
            
def {}():
    print("hello world")
    
    
AddScriptHook({}, MAIN_AFTER)
""".format(filename,filename))

    def generate_definitions_file(self):
        gbls = {}
        filename = self.file
        spl = filename.split(".")

        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])
        inf = os.path.join(self.cfg['MAP_FOLDER'], self.file, "war3map.lua")
        print("Generating python definitions from map source: {}.".format(inf))
        with open(inf, "r") as f:
            for match in re.findall(r"^[\s]*(gg_[^\s]+) = (.+)$", "".join(f.readlines()), flags=re.MULTILINE):
                gbls[match[0]] = match[1]
        outf = "{}.py".format(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], self.cfg['DEF_SUBFOLDER'], filename))
        with open(outf, "w") as f:
            f.write("# --DO NOT INCLUDE--\n")
            f.write("from .commonj import *\n")
            f.write("from .blizzardj import *\n")
            f.write("from .commonai import *\n")
            for var in gbls:
                f.write("{} = {}\n".format(var, gbls[var]))
        print("Definitions created in {}".format(outf))