
import os
import subprocess
import re
from pythonlua.translator import Translator
import shutil
import json
from .obj import ObjFile, DooFile, DataFile
import importlib
import sys
class Map:
    def __init__(self, file, **kwargs):
        try:
            with open("config.json","r") as f:
                self.cfg = json.load(f)
        except FileNotFoundError:
            raise SystemError("Configuration file config.json not found!")
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
        sys.path.append('pysrc')

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
            bf = '{}.pywc3.backup'.format(f)
            print("Backing up map to {}".format(bf))
            if os.path.isdir(f):
                if os.path.exists(bf):
                    shutil.rmtree(bf)
                shutil.copytree(f,bf)
            else:
                try: os.remove(bf)
                except: pass
                shutil.copy(f,bf)
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

    def translate_file(self, file, freeze_preproc = False):
        '''
        Translate a python script to lua. Also check for preprocessor calls such as """ObjEditor..."""
        '''
        with open(file, "r") as f:
            content = "".join(f.readlines())
        rc = content
        content = re.sub("^import (.+)$", "", content, flags=re.MULTILINE)
        content = re.sub("^from (.+) import (.+)*", "", content, flags=re.MULTILINE)

        # preprocess
        if re.match("^\s*#\s*RunPy=([\S]+?)\s*$",content,flags=re.MULTILINE):
            for fn in re.findall("^\s*#\s*RunPy=([\S]+?)\s*$", content, flags=re.MULTILINE):
                if fn.split('.')[-1] == "py":
                    fn = fn.split('.')[0].replace("\\",".")
                    if freeze_preproc:
                        print('> Freezing preprocess {}.py'.format(fn))
                    else:
                        print('> Preprocessing {}.py'.format(fn))
                    try: imp = importlib.import_module(fn)
                    except ModuleNotFoundError: raise SystemError('Module {} not found!'.format(fn))
                    imp.main(self)
            if freeze_preproc:
                rc = re.sub(r"^\s*#\s*RunPy=([\S]+?)\s*$",r"# frozen[RunPy=\1]",rc, flags=re.MULTILINE)
                with open(file,"w") as f:
                    f.write(rc)
        if freeze_preproc: return ""
        # object editing
        for fn in re.findall("^\s*#ObjEditor=([\S]+?)\s*$", content, flags=re.MULTILINE):
            if fn.split('.')[-1] == "json":
                fn = os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'],fn)
                try:
                    with open(fn,"r") as f:
                        c = "".join(f.readlines())
                        self.objeditor(c)
                except FileNotFoundError:
                    raise SystemError("ObjEditor json file {} not found in {}!".format(fn,os.getcwd()))
        for c in re.findall("\'{3}ObjEditor([\s\S]+?)\'{3}", content, flags=re.MULTILINE):
            self.objeditor(c)
        for c in re.findall("\"{3}ObjEditor([\s\S]+?)\"{3}", content, flags=re.MULTILINE):
            self.objeditor(c)
        try:
            lua = self.translator.translate(content)
        except RuntimeError as err:
            print('Error in file {}: {}'.format(file,err))
            raise
        return lua


    def import_tree_to_list(self,lst):
        '''
        Flatten the tree structure to a sorted import list
        '''
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


    def get_dependencies(self, file, current_list=[], exclude=True):
        '''
        find the imports in files and add them to a tree structure
        '''
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
                flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
                if file in flatten(current_list):
                    return lst
                rematcher = [
                    re.findall("^import (.+)", content, re.MULTILINE),
                    re.findall("^from (.+) import", content, re.MULTILINE),
                ]
                for matches in rematcher:
                    for match in matches:
                        newfile = re.sub('(?<!\.)\.(?!\.)', r'\\', match).strip('\\')
                        newfile = re.sub(r'\.\.\.\.', r'..\\..\\..\\', newfile)
                        newfile = re.sub(r'\.\.\.', r'..\..\\', newfile)
                        newfile = re.sub(r'\.\.', r'..\\', newfile)
                        path = os.path.normpath(os.path.join(srcdir, newfile))
                        if os.path.isdir(path):
                            for root,dir,files in os.walk(path):
                                for f in files:
                                    if f.split('.')[-1] == 'py' and f != '__init__.py':
                                        # print(os.path.join(path,f))
                                        for d in self.get_dependencies(os.path.join(root,f), lst, exclude=False):
                                            lst[-1].append(d)
                        else:
                            path = "{}.py".format(path)
                            if os.path.isfile(path):
                                for d in self.get_dependencies(path, lst, exclude=False):
                                    # if d not in lst:
                                    lst[-1].append(d)

        except FileNotFoundError:
            if 'math' not in file:
                print("WARNING: cannot find python source file {}".format(file))
        try: return lst
        except: return []

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
                f.write("-- Original map code\n")
                f.write("".join(f2.readlines()))
                f.write("\n")
            # write lua functions for pythonlua
            print("> Writing lua header...")
            f.write(Translator.get_luainit())
            # write python required libraries
            if not os.path.exists(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))):
                self.generate_python_source()
            for file in self.import_tree_to_list(self.get_dependencies(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename)))):
                f.write("-- Imported module {}\n".format(file))
                f.write(self.translate_file(file))
                print("> Appended translated file {}.".format(file))
                f.write("\n")
            # write
            f.write("-- Main map code\n")
            f.write(self.translate_file(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))
            print("> Appended translated file {}.".format(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename))))


    def unpack_to(self,dst):
        self.tmp_path = dst
        self.src_path = '{}/src'.format(self.tmp_path)
        self.dist_path = '{}/dist'.format(self.tmp_path)
        print("> Generating distribution map files...")
        # generate temp folder and paste all files there. If the map is an MPQ, extract all files.
        fn = os.path.join(self.cfg['MAP_FOLDER'], self.file)
        if os.path.exists(self.tmp_path):
            shutil.rmtree(self.tmp_path)
        if self._is_mpq:
            if not os.path.exists(self.tmp_path):
                os.mkdir(self.tmp_path)
                if not os.path.exists(self.src_path):
                    os.mkdir(self.src_path)
                if not os.path.exists(self.dist_path):
                    os.mkdir(self.dist_path)
            if not os.path.isfile(fn) and os.path.isfile(self.cfg['MPQ_EXE']):
                raise SystemError("Map file is an mpq archive and MPQEditor.exe does not exist.")
            self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'e', fn, '*', self.src_path, '/fp'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE))
        else:
            shutil.copytree(fn,self.src_path)
            os.mkdir(self.dist_path)
        if not os.path.exists('{}/war3map.lua'.format(self.src_path)):
            raise SystemError("Map does not include lua script. Please edit the map and choose lua as scripting language.")

    def dist_to(self,dst):
        # delete previous dist
        dst = os.path.join(dst, self.file)
        try: shutil.rmtree(dst)
        except: pass  # the dist map does not exist yet, no problem!
        try: os.remove(dst)
        except FileNotFoundError: pass  # no problem, carry on

        # Copy the temporary directories to the dist folder and include the built files. Save as MPQ if desired.
        if self._save_mpq:
            if not os.path.isfile(self.cfg['MPQ_EXE']):
                raise SystemError("Map file is an mpq archive and MPQEditor.exe does not exist.")
            # create mpq archive from folder
            self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'n', dst],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE))

            for root,dir,files in os.walk(self.src_path):
                for file in files:
                    nroot = root.replace(self.src_path, '').lstrip('\\')
                    self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'a', dst, os.path.join(root,file), os.path.join(nroot,file)],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE))
            for root,dir,files in os.walk(self.dist_path):
                for file in files:
                    nroot = root.replace(self.dist_path, '').lstrip('\\')
                    self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'a', dst, os.path.join(root,file), os.path.join(nroot,file)],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE))
        else:
            # copy the map
            shutil.copytree(self.src_path, dst)
            for root, dir, files in os.walk(self.dist_path):
                for file in files:
                    nroot = root.replace(self.dist_path, '').lstrip('\\')
                    shutil.copy(os.path.join(root,file),os.path.join(dst, nroot, file))
        # remove the temp directory
        try: shutil.rmtree(self.tmp_path)
        except: pass  # no problem

    def build(self):
        self.unpack_to(self.cfg['TEMP_FOLDER'])
        # Build the map from the temporary src to dist folder.
        self.build_script(
            '{}/war3map.lua'.format(self.src_path),
            '{}/war3map.lua'.format(self.dist_path),
        )
        # Build the ObjFiles, if they have been found in build_script.
        for objfile in self.objfiles:
            objf = self.objfiles[objfile]
            print("> Building ObjFile {}...".format(objf.filename))
            objf.write(self.dist_path)

        self.dist_to(self.cfg['DIST_FOLDER'])
        print("Build completed.")

    def freeze_preprocess(self):
        # remove extension if required
        self.unpack_to(self.cfg['TEMP_FOLDER'])
        filename = self.file
        spl = filename.split(".")
        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])
        self.translate_file(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename)), freeze_preproc=True)
        for file in self.import_tree_to_list(self.get_dependencies(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], "{}.py".format(filename)))):
            self.translate_file(file, freeze_preproc=True)
        self.dist_to(self.cfg['MAP_FOLDER'])

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
from {}.{} import *
            
            
def {}():
    print("hello world")
    
    
AddScriptHook({}, MAIN_AFTER)
""".format(self.cfg['DEF_SUBFOLDER'],filename,filename,filename))

    def generate_definitions_file(self):
        gbls = {}
        filename = self.file
        spl = filename.split(".")
        if spl[-1] == 'w3m' or spl[-1] == 'w3x':
            filename = ".".join(spl[:-1])
        temp = self.cfg['TEMP_FOLDER']
        fn = os.path.join(self.cfg['MAP_FOLDER'], self.file)
        if os.path.exists(temp):
            shutil.rmtree(temp)
        if self._is_mpq:
            if not os.path.exists(temp):
                os.mkdir(temp)
                if not os.path.exists('{}/src'.format(temp)):
                    os.mkdir('{}/src'.format(temp))
                if not os.path.exists('{}/dist'.format(temp)):
                    os.mkdir('{}/dist'.format(temp))
            if not os.path.isfile(fn) and os.path.isfile(self.cfg['MPQ_EXE']):
                raise SystemError("Map file is an mpq archive and MPQEditor.exe does not exist.")
            self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'e', fn, 'war3map.lua', '{}/src'.format(temp)],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE))
            self._print_sp(subprocess.Popen([self.cfg['MPQ_EXE'], 'e', fn, 'war3map.doo', '{}/src'.format(temp)],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE))
        else:
            if not os.path.exists(temp):
                os.mkdir(temp)
                if not os.path.exists('{}/src'.format(temp)):
                    os.mkdir('{}/src'.format(temp))
                if not os.path.exists('{}/dist'.format(temp)):
                    os.mkdir('{}/dist'.format(temp))
            try:
                shutil.copy(os.path.join(fn, 'war3map.lua'),'temp/src/war3map.lua')
                shutil.copy(os.path.join(fn, 'war3map.doo'), 'temp/src/war3map.doo')
            except: pass

        inf = 'temp/src/war3map.lua'
        print("Generating python definitions from map source: {}.".format(inf))
        try:
            with open(inf, "r") as f:
                for match in re.findall(r"^[\s]*(gg_[^\s]+) = (.+)$", "".join(f.readlines()), flags=re.MULTILINE):
                    gbls[match[0]] = match[1]
        except:
            print("Could not generate definitions, map does not have war3map.lua")
            shutil.rmtree(temp)
            return
        outf = "{}.py".format(os.path.join(self.cfg['PYTHON_SOURCE_FOLDER'], self.cfg['DEF_SUBFOLDER'], filename))
        with open(outf, "w") as f:
            f.write("# --DO NOT INCLUDE--\n")
            f.write("from .commonj import *\n")
            f.write("from .blizzardj import *\n")
            f.write("from .commonai import *\n")
            for var in gbls:
                f.write("{} = {}\n".format(var, gbls[var]))
            if self.cfg['READ_DOO']:
                df = DooFile()
                df.read('{}/src'.format(temp))
                if len(df.data['doo']) > 0:
                    f.write("\n# Below are the preplaced doodads\n\n")
                for doo in df.data['doo']:
                    doo['id'] = doo['id'].decode('utf-8')
                    doo['angle'] = doo['angle'] * 57.2958  # rad2deg
                    f.write('# {id}_{we_id} variation {var} at position ({x:.4g}, {y:.4g}, {z:.4g}), scale ({sx:.4g}, {sy:.4g}, {sz:.4g}), angle {angle:.4g}\n'.format(**doo))
                if len(df.data['cliff']) > 0:
                    f.write("\n# Below are the preplaced cliff/terrain doodads\n\n")
                for doo in df.data['cliff']:
                    doo['id'] = doo['id'].decode('utf-8')
                    f.write('# {id} at position ({x}, {y}, {z})\n'.format(**doo))
        print("Definitions created in {}".format(outf))

        shutil.rmtree(temp)