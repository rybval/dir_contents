import os
import sys

class Item:
    def _normCase(path_string):
        if sys.platform == 'win32':
            return path_string.casefold()
        else:
            return path_string

    def getSize(self):  return self.__size
    def getName(self):  return self.__name
    def getPath(self):
        return os.path.join(self.__parent.getPath(), self.__name())
    
    def __init__(self, name, parent):
        self.__name = name
        self.__parent = parent
        self.__size = None


class File(Item):
    def getHash(self):  return self.__hash
    def getInode(self): return self.__inode
    
    def __init__(self, name, parent):
        Item.__init__(self, name, parent)
        self.__hash = None
        self.__inode = None
        os.stat(os.path)


class Dir(Item):
    def getContent(self): return self.__content
    def getFiles(self):
        pass
    def gerDirs(self):
        pass
    def __init__(self, name, parent, skeleton = False):
        Item.__init__(self, name, parent)
        self.__content = tuple()
        

class Root(Directory):
    def _normPath(path):
        while path.endswith(os.sep):
            path = path[:-1]
        return path
        
    def getPath(self):
        return os.path.join(self.__parentdir, self.__name())
 
    def __init__(self, path, skeleton = False):
        path = self._normPath(path)
        self.__parentdir = path.dirname()
        Directory.__init__(self, path.basename(), None, skeleton)

        
