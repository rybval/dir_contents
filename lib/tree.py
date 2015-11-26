import os
import sys
from hashlib import sha1

class Item:
    def _normCase(path_string):
        if sys.platform == 'win32':
            return path_string.casefold()
        else:
            return path_string
            
    def findSize(self): pass
    def findHash(self): pass
    def getName(self):  return self._name
    
    def getSize(self):
        if self._size == None:
            self.findSize()
        return self._size
        
    def getHash(self):
        if self._hash == None:
            self.findHash()    
        return self._hash
        
    def getPath(self):
        return os.path.join(self._parent.getPath(), self._name)
    
    def __init__(self, name, parent):
        self._name = name
        self._parent = parent
        self._size = None
        self._hash = None


class File(Item):

    def_chunksize = 2**20
    
    def findSize(self):
        self._size = os.path.getsize(self.getPath())
        
    def findStat(self):
        statinfo = os.stat(self.getPath())
        self._size = statinfo.st_size
        self._inode = statinfo.st_ino
        self._device = statinfo.st_dev
        self._hlinks = statinfo.st_nlink
        
    def findHash(self, chunksize = def_chunksize):
        h = sha1()
        with open(self.getPath(), 'rb') as fd:
            while True:
                chunk = fd.read(chunksize)
                if chunk:
                    h.update(chunk)
                else:
                    return h.hexdigest()
            
    def getInode(self):
        if self._inode == None:
            self.findStat()
        return self._inode
        
    def getDevice(self): 
        if self._device == None:
            self.findStat()
        return self._device

    def getHardlinks(self):
        if self._hlinks == None:
            self.findStat()
        return self._hlinks
        
    def __init__(self, name, parent, find_size, find_inode, find_hash):
        Item.__init__(self, name, parent)
        self._inode = None
        self._device = None
        self._hlinks = None
        
        if find_inode:
            self.findStat()
        elif find_size:
            self.findSize()
            
        if find_hash:
            self.findHash()

class Dir(Item):
    def findSize(self):
        size = 0
        for item in self._content:
            size += item.getSize()
        self._size = size
        
    def getContent(self): 
        return self._content
        
    def getFiles(self):
        return tuple(i for i in self._content if type(i) is File)
        
    def getDirs(self):
        return tuple(i for i in self._content if type(i) is Dir)
        
    def __init__(self, name, parent, find_sizes, find_inodes, find_hashes):
        Item.__init__(self, name, parent)
        content = []
        path = self.getPath()
        for name in os.listdir(path):
            ip = os.path.join(path, name)
            if os.path.isdir(ip):
                content.append(Dir(name, self, find_sizes, 
                                                     find_inodes, find_hashes))
            elif os.path.isfile(ip):
                content.append(File(name, self, find_sizes, 
                                                     find_inodes, find_hashes))
        self._content = tuple(content)
        

class Root(Dir):
    def _normPath(self, path):
        while path.endswith(os.sep):
            path = path[:-1]
        return path
        
    def getPath(self):
        return os.path.join(self._parentdir, self._name)
 
    def __init__(self, path, find_sizes=False, 
                 find_inodes=False, find_hashes=False):
        path = self._normPath(path)
        self._parentdir = os.path.dirname(path)
        Dir.__init__(self, os.path.basename(path), None,
                           find_sizes, find_inodes, find_hashes)