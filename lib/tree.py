import os
import sys

class Item:
    def _normCase(path_string):
        if sys.platform == 'win32':
            return path_string.casefold()
        else:
            return path_string
    def findSize(self): pass
    def getSize(self):
        if self.__size == None:
            self.findSize()        
        return self.__size
    def getName(self):  return self.__name
    def getHash(self):  return self.__hash
    def getPath(self):
        return os.path.join(self.__parent.getPath(), self.__name())
    
    def __init__(self, name, parent):
        self.__name = name
        self.__parent = parent
        self.__size = None
        self.__hash = None


class File(Item):
    def findSize(self):
        self.__size = os.path.getsize(self.getPath())
        
    def getInode(self): return self.__inode
    def getDevice(self): return self.__device
    def getHardlinks(self): return self.__hlinks
    def __init__(self, name, parent):
        Item.__init__(self, name, parent, find_size, find_inode, find_hash)
        self.__inode = None
        self.__device = None
        self.__hlinks = None
        os.stat(os.path)


class Dir(Item):
    def findSize(self):
        size = 0
        for item in self.__content:
            size += item.getSize()
        self.__size = size
        
    def getContent(self): return self.__content
    def getFiles(self):
        return tuple(i for i in self.__content if type(i) is File) 
    def getDirs(self):
        return tuple(i for i in self.__content if type(i) is Dir)
    def __init__(self, name, parent, find_sizes, find_inodes, find_hashes):
        Item.__init__(self, name, parent)
        self.__content = tuple()
        

class Root(Directory):
    def _normPath(path):
        while path.endswith(os.sep):
            path = path[:-1]
        return path
        
    def getPath(self):
        return os.path.join(self.__parentdir, self.__name())
 
    def __init__(self, path, find_sizes=False, 
                 find_inodes=False, find_hashes=False):
        path = self._normPath(path)
        self.__parentdir = path.dirname()
        Dir.__init__(self, path.basename(), None,
                           find_sizes, find_inodes, find_hashes)
        

        
