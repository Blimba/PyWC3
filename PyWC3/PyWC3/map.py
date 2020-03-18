
import os
import subprocess
import re
from pythonlua.translator import Translator
import shutil
import json
from PyWC3.obj import ObjFile

class Map:
    def __init__(self, file, **kwargs):
        with open("config.json","r") as f:
            self.cfg = json.load(f)
        self._save_mpq = kwargs.get('save_mpq',self.cfg['SAVE_AS_MPQ'])
        if os.path.exists(os.path.join(self.cfg['MAP_FOLDER'], file)):
            self.file = file
            if(os.path.isdir(os.path.join(self.cfg['MAP_FOLDER'], file))):
                self._is_mpq = False
            else:
                self._is_mpq = True
                if not os.path.exists(self.cfg['MPQ_EXE']):
                    raise Exception("Cannot use MPQ mapfiles without MPQEditor. Please save your map as a folder format")
            # make a translator object with the main and config added to the currect context so it doesn't output them as local
            self.translator = Translator(locals=['main', 'config'], show_ast=kwargs.get('show_ast',False))
        else:
            raise Exception("Mapfile {} not found!".format(os.path.join(os.getcwd(),self.cfg['MAP_FOLDER'], file)))
        self.objfiles = {}

    def _print_sp(self,proc):
        output = []
        while True:
            line = proc.stdout.readline()
            if line == b"":
                break
            else:
                output.append(line.decode("utf-8"))
        while True:
            line = proc.stderr.readline()
            if line == b"":
                break
            else:
                output.append(line.decode("utf-8"))
        output = "".join(output)
        if output:
            print(output)


    def run(self):
        f = os.path.join(os.getcwd(),"{}\\{}".format(self.cfg['DIST_FOLDER'], self.file))
        if os.path.exists(f):
            print("Launching map {}".format(f))
            process = subprocess.Popen([self.cfg['WAR3_EXE'], '-launch', '-loadfile', '{}'.format(f), '-windowmode',self.cfg['WINDOWMODE']],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
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
        else:
            raise Exception("Mapfile {} not found!".format(os.path.join(self.cfg['MAP_FOLDER'], self.file)))


    def objeditor(self,c):
        try: js = json.loads(c)
        except json.decoder.JSONDecodeError as error: raise SystemError('Error in ObjEditor, error in json:\n{}'.format(error))
        for file in js:
            if not file in self.objfiles:
                self.objfiles[file] = ObjFile(file)
                try: self.objfiles[file].read(os.path.join(self.cfg['MAP_FOLDER'],self.file))
                except FileNotFoundError: pass
            for rawcode in js[file]:
                try:
                    ids = rawcode.split('>')
                    old_id = ids[0]
                    new_id = ids[-1]
                except: raise SystemError('Error in ObjEditor, do not understand rawcode {}'.format(rawcode))
                if new_id == old_id:
                    old_id = 0
                else:
                    old_id = bytes(old_id, encoding='utf-8')
                new_id = bytes(new_id,encoding='utf-8')
                for mod in js[file][rawcode]:
                    id = bytes(mod, encoding='utf-8')
                    value = js[file][rawcode][mod]
                    level = 0
                    pointer = 0
                    if isinstance(value,list):
                        for ivalue in value:
                            if isinstance(ivalue, dict):
                                level = ivalue['level']
                                pointer = ivalue['pointer']
                                value = ivalue['value']
                            self.objfiles[file].add_mod(new_id, id, ivalue, level, pointer, from_id=old_id)
                    if isinstance(value,dict):
                        level = value['level']
                        pointer = value['pointer']
                        value = value['value']
                    self.objfiles[file].add_mod(new_id,id,value,level,pointer,from_id=old_id)

    def translate_file(self, file):
        # print("> Translating file {}...".format(file))
        with open(file, "r") as f:
            content = "".join(f.readlines())
        content = re.sub("^import (.+)$", "", content, flags=re.MULTILINE)
        content = re.sub("^from (.+) import (.+)*", "", content, flags=re.MULTILINE)
        for c in re.findall("\'{3}ObjEditor([\s\S]+?)\'{3}", content, flags=re.MULTILINE):
            self.objeditor(c)
        for c in re.findall("\"{3}ObjEditor([\s\S]+?)\"{3}", content, flags=re.MULTILINE):
            self.objeditor(c)
        return self.translator.translate(content)


    def import_tree_to_list(self,lst):
        flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
        def unique(l):
            rl = []
            for i in l:
                if i not in rl:
                    rl.append(i)
            return rl
        nfilelst = unique(flatten(lst))
        try:
            while isinstance(lst[0][0],list):
                lst = lst[0]
        except:
            pass
        def iterator(lvl,lst,parents):
            for item in lst:
                if isinstance(item,str):
                    for parent in parents:
                        i1 = nfilelst.index(item)
                        i2 = nfilelst.index(parent)
                        if i1 > i2:
                            nfilelst[i1], nfilelst[i2] = nfilelst[i2], nfilelst[i1]
                    parents.append(item)
                elif isinstance(item,list):
                    iterator(lvl+">",item,parents.copy())
        for i in lst:
            iterator('',i,[])
        return nfilelst

    def get_dependencies(self, file, exclude=True):
        # print("> Reading file {}...".format(file))
        try:
            with open(file, "r") as f:
                lst = []
                content = "".join(f.readlines())
                srcdir = os.path.dirname(file)
                # exclude files containing python only code
                if re.match("^#.*DO NOT INCLUDE.*$", content, flags=re.MULTILINE):
                    return []
                if not exclude:
                    lst.append([file])
                else:
                    lst.append([])

                rematcher = [
                    re.findall("^import (.+)", content, re.MULTILINE),
                    re.findall("^from (.+) import", content, re.MULTILINE),
                ]
                for matches in rematcher:
                    for match in matches:
                        newfile = re.sub('(?<!\.)\.(?!\.)', '\\\\', match).strip('\\')
                        newfile = re.sub('\.\.', '..\\\\', newfile)
                        path = os.path.normpath(os.path.join(srcdir, newfile))
                        for d in self.get_dependencies("{}.py".format(path), exclude=False):
                            # if d not in lst:
                            lst[-1].append(d)

        except FileNotFoundError:
            if 'math' not in file:
                print("WARNING: cannot find python source file {}".format(file))
        try: return lst
        except: return []

    def get_war3maplua(self):
        if self._is_mpq:
            if(not os.path.exists('temp/war3map.lua')):
                if not os.path.exists('temp'):
                    os.mkdir('temp')
                self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'e', os.path.join(self.cfg['MAP_FOLDER'], self.file), 'war3map.lua'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE))
                os.rename('war3map.lua','temp/war3map.lua')
            return 'temp/war3map.lua'
        else:
            return os.path.join(self.cfg['MAP_FOLDER'], self.file, "war3map.lua")

    def build_script(self,src,dst):
        # remove extension if required
        filename = self.file
        spl = filename.split(".")
        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])

        # write translated lua files
        with open(dst, "w") as f:
            # write map code
            with open(src, "r") as f2:
                f.write("-- Generated map code\n")
                f.write("".join(f2.readlines()))
                f.write("\n")
            # write lua functions for pythonlua
            print("> Writing lua header...")
            f.write(Translator.get_luainit())
            # write python required libraries
            for file in self.import_tree_to_list(self.get_dependencies(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename)))):
                f.write("-- Imported module {}\n".format(file))
                f.write(self.translate_file(file))
                print("> Appended translated file {}.".format(file))
                f.write("\n")
            # write
            f.write("-- Main map code\n")
            f.write(self.translate_file(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))
            print("> Appended translated file {}.".format(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))


    def build(self):
        # delete previous dist
        try: shutil.rmtree(os.path.join(self.cfg['DIST_FOLDER'], self.file))
        except: pass  # the dist map does not exist yet, no problem!
        try: os.remove(os.path.join(self.cfg['DIST_FOLDER'], self.file))
        except FileNotFoundError: pass  # no problem, carry on

        print("> Generating distribution map files...")
        fn = os.path.join(self.cfg['MAP_FOLDER'], self.file)
        if self._save_mpq:
            self.build_script(
                self.get_war3maplua(),
                'war3map.lua'
            )

            # if we start out as a file
            if self._is_mpq:
                nfn = os.path.join(self.cfg['DIST_FOLDER'], self.file)
                shutil.copyfile(fn, nfn)
            else:
                # create mpq archive from folder
                nfn = os.path.join(self.cfg['DIST_FOLDER'], self.file)
                self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'n', nfn],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE))
                for root,dir,files in os.walk(fn):
                    for file in files:
                        nroot = root.replace(fn, '').lstrip('\\')
                        self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'a', nfn, os.path.join(root,file), os.path.join(nroot,file)],
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE))
            # add the new script to the mpq
            self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'a', nfn, 'war3map.lua'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE))
            os.remove('war3map.lua')
        else:
            # copy the map
            if os.path.isfile(fn) and os.path.isfile(self.cfg['MPQ_EXE']):
                self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'e', fn, '*', 'temp'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE))
                shutil.copytree('temp',os.path.join(self.cfg['DIST_FOLDER'], self.file))
            elif os.path.isdir(fn):
                shutil.copytree(os.path.join(self.cfg['MAP_FOLDER'], self.file),os.path.join(self.cfg['DIST_FOLDER'], self.file))


            self.build_script(
                self.get_war3maplua(),
                os.path.join(self.cfg['DIST_FOLDER'], self.file, "war3map.lua")
            )
            for objfile in self.objfiles:
                objf = self.objfiles[objfile]
                print("> Building ObjFile {}...".format(objf.filename))
                objf.write(os.path.join(self.cfg['DIST_FOLDER'], self.file))

        try: shutil.rmtree('temp')
        except: pass  # no problem
        print("Build completed.")


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
        inf = self.get_war3maplua()
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