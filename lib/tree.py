import os
import sys
from hashlib import sha1, sha256, sha512, md5
from binascii import unhexlify, hexlify

hash_chunksize = 2**20
hash_func = sha1

def _appendIfNotNone(dict, key, data):
    if data != None:
        dict[key] = data
    
def _normPath(path):
    if sys.platform == 'win32':
        path = path.replace('/','\\')
    while path.endswith(os.sep):
        path = path[:-1]
    return path

def _normCase(path_string):
    if sys.platform == 'win32':
        return path_string.casefold()
    else:
        return path_string

class Item():
    def isAccessible(self): return self._accessible
    def findSize(self): pass
    def findHash(self): pass
    def getName(self): return self._name
    def getSize(self): return self._size
    def getHashFunc(self):
        return self._parent.getHashFunc()

    def getHash(self, as_hex=True, func=None):
        if self._hash is None or (func and self.getHashFunc() != func):
            self.findHash(func)
        if as_hex:
            return self._hash
        else:
            return unhexlify(self._hash)

    def getPath(self):
        return os.path.join(self._parent.getPath(), self._name)

    def __init__(self, name, parent, find_hash, accessible = True):
        self._accessible = accessible
        self._name = name
        self._parent = parent
        self.findSize()
        self._hash = None
        if find_hash:
            self.findHash()

    def __str__(self):
        return self.getName()
        
    def _findsizeof(self, list=[]):
        list += [self._accessible, self._name, self._size, self._hash]
        sizeof = 0
        for field in list:
            sizeof += sys.getsizeof(field)
        return sizeof
        
    def  __sizeof__(self):
        return self._findsizeof()

    def refresh(self):
        # need optimisation
        # добавить отдельное простое пересчитывание размера содержимого
        # (без системных вызовов, чтобы можно было refresh малую папку
        # и пересчитать размер родителя, а не рефрешить его полностью
        # или автоматически дёргать метод пересчёта родителя/root'а 
        # при рефреше подпапки)
        type_ = type(self)
        find_hash = False
        if self._hash != None:
            find_hash = True
        type_.__init__(self, self._name, self._parent, find_hash)
        
    def toDict(self):
        d = {
            'name' : self._name,
            'path' : self.getPath(),
            'accessible' : self._accessible,
            'type' : 'item'
        }
        
        _appendIfNotNone(d, 'size', self._size)
        _appendIfNotNone(d, 'hash', self._hash)
            
        return d


class File(Item):
    def findStat(self):
        try:
            statinfo = os.stat(self.getPath())
        except:
            self._accessible = False
            self._size = None
            self._inode = None
            self._device = None
            self._hlinks = None
        else:
            self._size = statinfo.st_size
            self._inode = statinfo.st_ino
            self._device = statinfo.st_dev
            self._hlinks = statinfo.st_nlink
    
    def findSize(self):
        self.findStat()
        
    def findHash(self, func=None, chunksize = hash_chunksize):
        if not func:
            func = self.getHashFunc()
        h = func()
        try: 
            fd = open(self.getPath(), 'rb')
        except:
            self._accessible = False
        else:
            while True:
                chunk = fd.read(chunksize)
                if chunk:
                    h.update(chunk)
                else:
                    self._hash = h.hexdigest()
                    break
            fd.close()
            
    def getInode(self): return self._inode  
    def getDevice(self): return self._device
    def getHardlinks(self): return self._hlinks
    
    def  __sizeof__(self):
        return self._findsizeof([self._inode, self._device, self._hlinks])
        
    def __init__(self, name, parent, find_hash):
        Item.__init__(self, name, parent, find_hash)
        
    def toDict(self):
        d = Item.toDict(self)
        d['type'] = 'file'
        _appendIfNotNone(d, 'inode', self._inode)
        _appendIfNotNone(d, 'device', self._device)
        _appendIfNotNone(d, 'hardlinks', self._hlinks)
        return d
        


class Dir(Item):
    def findSize(self):
        if not self._accessible:
            self._size = None
            return
        size = 0
        for item in self.getContent():
            if item.isAccessible():
                size += item.getSize()
        self._size = size
        
    def findHash(self, func=None):
        # hash is sha1 of XOR all _hashs of content
        # and _name (hash of _name excluded by default)
        if not self._accessible:
            self._hash = None
            return
        if not func:
            func = self.getHashFunc()
        h = func()
        #h.update(self._name.encode('utf8'))
        hash = h.hexdigest()
        for item in self.getContent():
            if item.isAccessible():
                hash = '{0:0>{1}x}'.format(
                        int(hash, 16) ^ int(item.getHash(func), 16), len(hash))
        self._hash = hash


    def getContent(self, cond_сallback=None, type_=None, 
                                    min_depth=1,  max_depth=1, count=False):
        if not isinstance(min_depth, int) or (isinstance(max_depth, int) 
                                                    and min_depth > max_depth):
            raise ValueError('min_depth must be an natural number')
        
        if count:
            out = 0
        else:
            out = []

        if min_depth == 1:
            if not type_:
                content = list(self._content)
            else:
                if isinstance(type(type_), str):
                    if type_.casefold() in ('dir', 'directory', 'folder'):
                        type_ = Dir
                    elif type_.casefold() == 'file':
                        type_ = File
                    elif type_.casefold() in ('n/d', 'item'):
                        type_ = Item
                    else:
                        raise ValueError('type_ must be "Dir", "File", ' 
                                         '"Item" or type() instance')
                elif type(type_) is not type:
                    raise ValueError('type_ must be "Dir", "File", "Item" '
                                     'or type() instance')
                
                content = [it for it in self._content if type(it) == type_]                        
            
            if not cond_сallback:
                if count:
                    out += len(content)
                else:
                    out += content
            else:
                for item in content:
                    if cond_сallback(item):
                        if count:
                            out += 1
                        else:
                            out += [item]
        elif min_depth > 1:
            min_depth -= 1

        if max_depth != 1:
            if isinstance(max_depth, int) and max_depth > 1:
                max_depth -= 1
            elif max_depth not in ('max', 'MAX', 'Max'):
                raise ValueError('depth must be an' 
                                 'natural number or "max"')
            for dir_ in self.getContent(type_ = Dir):
                out += dir_.getContent(cond_сallback, type_, 
                                               min_depth, max_depth, count)

        return out

    def __getitem__(self, key):
        key = _normCase(_normPath(key))
        if key == '.':
            return self
        else:
            result = self.getContent(
                                lambda item: _normCase(item.getName()) == key)
            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                raise KeyError('Element with this name not found')
            else:
                raise KeyError('More than one element have'
                                'this name in current dir')

    def getByPath(self, path):        
        path = _normCase(_normPath(path))
        if path.startswith(os.path.join(_normCase(self.getPath()),'')):
            path = '.' + path[len(self.getPath())-1:]
        
        if path.startswith('.'+os.sep):
            path = path[2:]
        else:
            return None

        chain = path.split(os.sep)
        level = self
        for name in chain:
            for item in level._content:
                if _normCase(item._name) == name:
                    level = item
                    break
            else:
                return None
        return level

        
    def __iter__(self):
       for item in self.getContent():
          yield item
          
    def __sizeof__(self):
        return self._findsizeof([self._content])

    def __init__(self, name, parent, find_hashes):
        self._parent = parent
        self._name = name
        content = []
        path = self.getPath()
        try:
            names = os.listdir(path)
        except:
            accessible = False
        else:
            accessible = True
            for name_ in names:
                ip = os.path.join(path, name_)
                if os.path.isdir(ip):
                    content.append(Dir(name_, self, find_hashes))
                elif os.path.isfile(ip):
                    content.append(File(name_, self, find_hashes))
                else:
                    content.append(Item(name_, self, find_hashes, False))
        self._content = tuple(content)
        Item.__init__(self, name, parent, find_hashes, accessible)
        
    def toDict(self):
        d = Item.toDict(self)
        d['type'] = 'directory'
        content = [item.toDict() for item in self.getContent()]
        _appendIfNotNone(d, 'content', content)
        return d


class Root(Dir):
    def getPath(self):
        return os.path.join(self._parentdir, self._name)

    def getHashFunc(self):
        return self._hash_func

    def __init__(self, path, find_hashes=False, hash_func_=hash_func):
        self._hash_func = hash_func_
        path = _normPath(path)
        parent = os.path.dirname(path)
        name = os.path.basename(path)
        if sys.platform == 'win32' and not name and ':' in parent:
            parent, name = name, parent + os.sep
        self._parentdir = parent
        Dir.__init__(self, name, None, find_hashes)

    def refresh(self):
        find_hash = False
        if self._hash != None:
            find_hash = True
        Root.__init__(self, self.getPath(), find_hash, self.getHashFunc())