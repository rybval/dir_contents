#!/usr/bin/env python3

"""Write to file hashes of all files, contaned in folder"""

import os
import sys
from hashlib import md5, sha1, sha256, sha512
from duplicatesfinder import getHashSum

if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = '.'
    
    repname = os.path.join(path, 'Hashes.txt')
    
    with open(repname, 'wt', encoding = 'utf-8') as file:
        for dirname, dirslist, filelist in os.walk(path):
            for filename in filelist:
                absfilename = os.path.join(dirname, filename)
                hashes = tuple(getHashSum(absfilename, hf) 
                                         for hf in (md5, sha1, sha256, sha512))
                size = os.path.getsize(absfilename)
                file.write('{}; {}; {}\n'.format(hashes, size, absfilename))
            
