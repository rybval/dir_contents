import os
import sys
from hashlib import sha1

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
    def findHash(self): return 'not implemented yet'
    def getName(self): return self._name
    def getSize(self): return self._size
        
    def getHash(self):
        if self._hash == None:
            self.findHash()    
        return self._hash
        
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

    hash_chunksize = 2**20
    
    def findStat(self):
        statinfo = os.stat(self.getPath())
        self._size = statinfo.st_size
        self._inode = statinfo.st_ino
        self._device = statinfo.st_dev
        self._hlinks = statinfo.st_nlink
    
    def findSize(self):
        self.findStat()
        
    def findHash(self, chunksize = hash_chunksize):
        h = sha1()
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
          
    def getItemsCount(self):
        return len(self._dirs) + len(self._files)
        
    def getFilesCount(self):
        return len(self._files)
        
    def getDirsCount(self):
        return len(self._dirs)
        
    def getItems(self): 
        return self._dirs + self._files
        
    def getFiles(self):
        return self._files
        
    def getDirs(self):
        return self._dirs
        
    def _getALLCount(self, thingname):
        thingname = thingname.rstrip('s')
        getThingsCount = Dir.__getattr__('get'+thingname+'sCount')
        getAllThingsCount = Dir.__getattr__('getALL'+thingname+'sCount')
        count = Dir.getThingsCount(self)
        for dir_ in self.getDirs():
            count += Dir.getAllThingsCount(dir_)
        return count
        
    def getAllItemsCount(self): return self._getALLCount('Items')
    def getAllFilesCount(self): return self._getALLCount('Files')
    def getAllDirsCount(self): return self._getALLCount('Dirs')
    
    def _getALL(self, thingname):
        thingname = thingname.rstrip('s')
        getThings = Dir.__getattr__('get'+thingname+'s')
        getAllThings = Dir.__getattr__('getALL'+thingname+'s')
        things = list(Dir.getThings(self))
        for dir_ in self.getDirs():
            things += list(Dir.getAllThings(dir_))
        return things
    
    def getAllItems(self): self._getALL('Items')
    def getAllFiles(self): self._getAll('Files')
    def getAllDirs(self): self._getAll('Dirs')
        
    def __init__(self, name, parent, find_hashes):
        self._parent = parent
        self._name = name
        files = []
        dirs = []
        path = self.getPath()
        for name in os.listdir(path):
            ip = os.path.join(path, name)
            if os.path.isdir(ip):
                dirs.append(Dir(name, self, find_hashes))
            elif os.path.isfile(ip):
                files.append(File(name, self, find_hashes))
        self._files = tuple(files)
        self._dirs = tuple(dirs)
        Item.__init__(self, name, parent, find_hashes)


class Root(Dir):
    def getPath(self):
        return os.path.join(self._parentdir, self._name)
 
    def __init__(self, path, find_hashes=False):
        path = _normPath(path)
        self._parentdir = os.path.dirname(path)
        Dir.__init__(self, os.path.basename(path), None, find_hashes)
                           
    def refresh(self, hashes=False):
        self = Root.__init__(self.getPath(), hashes)