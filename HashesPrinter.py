#!/usr/bin/env python3
import os
from hashlib import md5, sha1, sha256, sha512
from duplicatesfinder import getHashSum

if __name__ == '__main__':
    with open('Hashes.txt', 'wt', encoding = 'utf-8') as file:
        for dirname, dirslist, filelist in os.walk('.'):
            for filename in filelist:
                absfilename = dirname+'\\'+filename
                hashes = tuple(getHashSum(absfilename, hf) for hf in (md5, sha1, sha256, sha512))
                size = os.path.getsize(absfilename)
                file.write('{}; {}; {}\n'.format(hashes, size, absfilename))
            
