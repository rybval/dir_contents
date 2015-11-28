import os
import sys
from hashlib import sha1, sha256, sha512, md5
from binascii import unhexlify, hexlify

hash_chunksize = 2**20
hash_func = sha1

def _normPath(path):
    while path.endswith(os.sep):
        path = path[:-1]
    return path

def _normCase(path_string):
    if sys.platform == 'win32':
        return path_string.casefold()
    else:
        return path_string
    
class Item():
    def findSize(self): pass
    def findHash(self): pass
    def getName(self): return self._name
    def getSize(self): return self._size
    def getHashFunc(self):
        return self._parent.getHashFunc()
        
    def getHash(self, as_hex=True, func=None):
        if self._hash == None or self.getHashFunc != func:
            self.findHash(func)    
        if as_hex:
            return self._hash
        else:
            return unhexlify(self._hash)
        
    def getPath(self):
        return os.path.join(self._parent.getPath(), self._name)
    
    def __init__(self, name, parent, find_hash):
        self._name = name
        self._parent = parent
        self.findSize()
        self._hash = None
        if find_hash:
            self.findHash()
        
    def refresh(self):
        # need optimisation
        type_ = type(self)
        self = type_.__init__(self._name, self._parent)

        
class File(Item):
    def findStat(self):
        statinfo = os.stat(self.getPath())
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
        with open(self.getPath(), 'rb') as fd:
            while True:
                chunk = fd.read(chunksize)
                if chunk:
                    h.update(chunk)
                else:
                    self._hash = h.hexdigest()
                    return
            
    def getInode(self): return self._inode  
    def getDevice(self): return self._device
    def getHardlinks(self): return self._hlinks
        
    def __init__(self, name, parent, find_hash):
        Item.__init__(self, name, parent, find_hash)
            
class Dir(Item):
    def findSize(self):
        size = 0
        for item in (self._dirs + self._files):
            size += item.getSize()
        self._size = size
        
    def findHash(self, func=None):
        # hash is sha1 of XOR all _hashs of content
        # and _name (hash of _name excluded by default)
        if not func:
            func = self.getHashFunc()
        h = func()
        #h.update(self._name.encode('utf8'))
        hash = h.hexdigest()
        for item in self.getContent():
            hash = '{0:0>{1}x}'.format(
                        int(hash, 16) ^ int(item.getHash(func), 16), len(hash))
        self._hash = hash             
        
    def getContent(self, cond_сallback=lambda i: True, 
                                           type=Item, deep=False, count=False):
        if count:
            out = 0
        else:
            out = []

        if type == Item:
            content = self._dirs + self._files
        elif type == File:
            content = self._files
        elif type == Dir:
            content = self._dirs

        for item in content:
            if cond_сallback(item):
                if count:
                    out += 1
                else:
                    out.append(item)

        if deep:
            for dir_ in self._dirs:
                out += dir_.getContent(cond_сallback, type, True, count)

        return out
        
    def __init__(self, name, parent, find_hashes):
        self._parent = parent
        self._name = name
        files = []
        dirs = []
        path = self.getPath()
        for name_ in os.listdir(path):
            ip = os.path.join(path, name_)
            if os.path.isdir(ip):
                dirs.append(Dir(name_, self, find_hashes))
            elif os.path.isfile(ip):
                files.append(File(name_, self, find_hashes))
        self._files = tuple(files)
        self._dirs = tuple(dirs)
        Item.__init__(self, name, parent, find_hashes)


class Root(Dir):
    def getPath(self):
        return os.path.join(self._parentdir, self._name)
    
    def getHashFunc(self):
        return self._hash_func
 
    def __init__(self, path, find_hashes=False, hash_func_=hash_func):
        self._hash_func = hash_func_
        path = _normPath(path)
        self._parentdir = os.path.dirname(path)
        Dir.__init__(self, os.path.basename(path), None, find_hashes)
                           
    def refresh(self, hashes=False):
        self = Root.__init__(self.getPath(), hashes)