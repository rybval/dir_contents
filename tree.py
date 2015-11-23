import os
import sys

class Item:
    def _normalisePath(path_string):
        if sys.platform == 'win32':
            return path_string.casefold()
        else:
            return path_string
     
    def getSize(self):
        return __size
    
    def __init__(self, name):
        self.__name = name
        
class Directory:        
    def __init__(self, path, name=None, parent=None):
        
        
class File(Item):
    def __init__(self, name, parent=None):
        
        Item.__init__(self, name)