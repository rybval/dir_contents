import os
import sys

class FolderStats:
    def __init__(self, path):
        if sys.platform == 'win32':
            self.path = path.casefold()
        else:
            self.path = path
            
        if os.path.isfile(self.path):
            self.type = 'file'
        elif os.path.isdir(self.path):
            self.type = 'dir'
        else:
            self.type = None
        
        if self.type == 'file':
            self.size = os.path.getsize(self.path)
        elif self.type == 'dir':
            self.size = {
                'files' = f
            }
        
        self.size = {
            'files': None,
            'folders': None,
            'bytes': None
            }
        
        if self.type == 'file':
            self.size = 
        

            
        self.unaccessible = False
        self.tree = []