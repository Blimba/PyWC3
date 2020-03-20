
import struct
import json
import os


class DataFile:

    def traverse_init(self,format,ret):
        for key in format:
            if isinstance(format[key], dict):
                ret[key] = []
            else:
                ret[key] = 0

    def __init__(self,format,filename=None):
        self.filename = filename
        format = json.load(open(os.path.join("PyWC3\PyWC3", format)))
        self.format = format
        self.objs = {}
        self.traverse_init(self.format, self.objs)



    def read_var(self,fmt):
        if fmt == 'b':
            return self.f.read(1)
        elif struct.calcsize(fmt) > 1:
            return struct.unpack(fmt,self.f.read(struct.calcsize(fmt)))[0]
        else:
            # read a \0 terminated string
            str = b""
            while True:
                byte = self.f.read(1)
                str += byte
                if byte == b"\x00":
                    break
            return struct.unpack("{}{}".format(len(str),fmt),str)[0][:-1].decode('utf-8')

    def traverse_read(self, format, ret):
        for key in format:
            if isinstance(format[key], dict):
                i = 1
                if 'num_{}'.format(key) in ret:
                    i = ret['num_{}'.format(key)]
                    if i == "<i": i = 1
                    lst = []
                    for _ in range(i):
                        tmp = {}
                        self.traverse_read(format[key], tmp)
                        lst.append(tmp)
                    ret[key] = lst
                else:
                    ret[key] = self.traverse_read(format[key], {})
            else:
                try:
                    struct.calcsize(format[key])
                    ret[key] = self.read_var(format[key])
                except:
                    ret[key] = self.read_var(ObjFile.var_types[ret[format[key]]])

    def read(self,path='.',filename=None):
        if not filename:
            filename = os.path.join(path,self.filename)
        with open(filename,"rb") as self.f:
            self.objs = {}
            self.traverse_read(self.format,self.objs)

    def write_var(self,var,fmt):
        if isinstance(var,int):
            w = struct.pack("<i",var)
        elif isinstance(var,bytes):
            if len(var)==1:
                w = var
            else:
                w = struct.pack("{}s".format(len(var)),var)
        elif isinstance(var,float):
            w = struct.pack("<f", var)
        elif isinstance(var,str):
            var = var.encode('utf-8')
            var += b"\x00"
            w = struct.pack("{}s".format(len(var)), var)
        else:
            raise SystemError("Unknown type passed to write_var: {}".format(type(var)))
        self.f.write(w)

    def traverse_write(self,format,values):
        for key in format:
            if isinstance(format[key], dict):
                for item in values[key]:
                    self.traverse_write(format[key],item)
            else:
                self.write_var(values[key],format[key])

    def write(self,path='.'):
        filename = os.path.join(path, self.filename)
        with open(filename,"wb") as self.f:
            self.traverse_write(self.format, self.objs)




class ObjFile(DataFile):
    var_types = {
        0: "<i",
        1: "<f",
        2: "<f",
        3: "s",
    }
    formats = {
        'w3a': 'obj_format_ex.json',  # ability
        'w3d': 'obj_format_ex.json',  # doodad
        'w3q': 'obj_format_ex.json',  # upgrade
        'w3u': 'obj_format.json',  # unit
        'w3t': 'obj_format.json',  # item
        'w3b': 'obj_format.json',  # destructable
        'w3h': 'obj_format.json',  # buff
    }
    files = {
        'ability': 'war3map.w3a',
        'doodad': 'war3map.w3d',
        'upgrade': 'war3map.w3q',
        'unit': 'war3map.w3u',
        'item': 'war3map.w3t',
        'destructable': 'war3map.w3b',
        'buff': 'war3map.w3h',
    }

    def __init__(self, format):
        super().__init__(ObjFile.formats[ObjFile.files[format].split('.')[-1]],ObjFile.files[format])
        self.objs['version'] = b"\x02\x00\x00\x00"

    def remove_obj(self,id):
        for obj in self.objs['edited']:
            if obj['old_id'] == id:
                self.objs['edited'].remove(obj)
                self.objs['num_edited'] -= 1
                return True
        for obj in self.objs['custom']:
            if obj['new_id'] == id:
                self.objs['custom'].remove(obj)
                self.objs['num_custom'] -= 1
                return True
        return False

    def remove_mod(self,obj_id,mod_id):
        for obj in self.objs['edited']:
            if obj['old_id'] == obj_id:
                for mod in obj['mods']:
                    if mod['id'] == mod_id:
                        obj['mods'].remove(mod)
                        obj['num_mods']-=1
                        if obj['num_mods'] == 0:
                            self.objs['edited'].remove(obj)
                            self.objs['num_edited'] -= 1
                        return True
        for obj in self.objs['custom']:
            if obj['new_id'] == obj_id:
                for mod in obj['mods']:
                    if mod['id'] == mod_id:
                        obj['mods'].remove(mod)
                        obj['num_mods'] -= 1
                        if obj['num_mods'] == 0:
                            self.objs['custom'].remove(obj)
                            self.objs['num_custom'] -= 1
                        return True
        return False

    def add_obj(self,obj_id,from_id=0):
        if from_id:
            self.objs['num_custom'] += 1
            dct = {}
            self.traverse_init(self.format['custom'],dct)
            dct['old_id'] = from_id
            dct['new_id'] = obj_id
            self.objs['custom'].append(dct)
        else:
            self.objs['num_edited'] += 1
            dct = {}
            self.traverse_init(self.format['edited'], dct)
            dct['old_id'] = obj_id
            dct['new_id'] = b"\x00\x00\x00\x00"
            self.objs['edited'].append(dct)

    def add_mod(self,obj_id,mod_id,value,level=0,pointer=0,from_id=0):
        for obj in self.objs['custom']:
            if obj['new_id'] == obj_id:
                for mod in obj['mods']:
                    if mod['id'] == mod_id:
                        mod['value'] = value
                        return True
                nmod = {
                    'id': mod_id,
                    'value': value,
                    'level': level,
                    'pointer': pointer,
                    'terminate': b'\x00\x00\x00\x00'
                }
                if isinstance(value, int) or isinstance(value, bytes): nmod['var_type'] = 0
                if isinstance(value, float): nmod['var_type'] = 2
                if isinstance(value, str): nmod['var_type'] = 3
                obj['mods'].append(nmod)
                obj['num_mods'] += 1
                return True

        for obj in self.objs['edited']:
            if obj['old_id'] == obj_id:
                for mod in obj['mods']:
                    if mod['id'] == mod_id:
                        mod['value'] = value
                        return True
                nmod = {
                    'id': mod_id,
                    'value': value,
                    'level': level,
                    'pointer': pointer,
                    'terminate': mod_id,
                }
                if isinstance(value, int) or isinstance(value, bytes): nmod['var_type'] = 0
                if isinstance(value, float): nmod['var_type'] = 2
                if isinstance(value, str): nmod['var_type'] = 3
                obj['mods'].append(nmod)
                obj['num_mods'] += 1
                return True
        self.add_obj(obj_id,from_id)
        self.add_mod(obj_id,mod_id,value,level,pointer,from_id=from_id)
        return True

class DooFile(DataFile):
    flags = {
        'custom_z': int('100',2),
        'visible': int('010',2),
        'invisible': int('001',2)
    }
    def __init__(self):
        super().__init__('doo_format.json','war3map.doo')

    def add_doo(self,id,x,y,z,var=0,a=0.0,sx=1.0,sy=1.0,sz=1.0,flags=None,life=100):
        x = float(x)
        y = float(y)
        z = float(z)
        a = float(a)
        sx = float(sx)
        sy = float(sy)
        sz = float(sz)
        var = int(var)
        if not flags:
            flags = DooFile.flags['custom_z'] | DooFile.flags['visible']
        flags = flags.to_bytes(1,'little')
        assert(isinstance(var,int))
        assert (isinstance(id, bytes))
        assert (isinstance(x, float))
        assert (isinstance(y, float))
        assert (isinstance(z, float))
        assert (isinstance(a, float))
        assert (isinstance(sx, float))
        assert (isinstance(sy, float))
        assert (isinstance(sz, float))
        assert (isinstance(flags, bytes) and len(flags) == 1)
        life = life.to_bytes(1,'little')
        assert (isinstance(life, bytes) and len(life) == 1)
        self.objs['num_doo'] += 1
        doos = self.objs['doo']
        doo = {
            'id': id,
            'var': var,
            'x': x,
            'y': y,
            'z': z,
            'angle': a / 57.2958,
            'sx': sx,
            'sy': sy,
            'sz': sz,
            'idagain': id,
            'ffff': b"\xFF\xFF\xFF\xFF",
            'flags': flags,
            'life': life,
            '0000': 0,
            'we_id': doos[-1]['we_id']+1,
        }
        doos.append(doo)