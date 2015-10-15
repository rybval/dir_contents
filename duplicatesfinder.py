#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3.4.3

import os
from hashlib import md5, sha1, sha256, sha512

def in_list_of_lists(ll, item):
    for list in ll:
        if item in list:
            return ll.index(list)+1
    return False

def getHashSum(fileName, hashfunc = md5, chunksize = 4096):
    h = hashfunc()
    with open(fileName, 'rb') as fd:
        while True:
            chunk = fd.read(chunksize)
            if chunk:
                h.update(chunk)
            else:
                return h.hexdigest()
                 
                
def compareFiles(filename_1, filename_2, chunksize = 4096):
    with open(filename_1, 'rb') as f1:
        with open(filename_2, 'rb') as f2:
            while True:
                chunk1 = f1.read(chunksize)
                chunk2 = f2.read(chunksize)
                if chunk1 != chunk2:
                    return False
                elif (not chunk1) and (not chunk2):
                    return True
                    
class FilesStructure:

    def _checkHashDuplicates(self):
        self._hash_dublicates, self._hash_unique = {}, {}
        for key in self._hashes:
            if len(self._hashes[key]) > 1:
                self._hash_dublicates[key] = self._hashes[key]
            elif len(self._hashes[key]) == 1:
                self._hash_unique[key] = self._hashes[key]

    def _renewDerivatives(self):
        self._checkHashDuplicates()
        self._duplicates = None
        self._unique = None

    def _addHashs(self, *roots):        
        for root in roots:
            for dirname, dirslist, filelist in os.walk(root):
                for filename in filelist:
                    absfilename = os.path.join(dirname, filename)
                    try:
                        hash = getHashSum(absfilename)
                        size = os.path.getsize(absfilename)
                    except:
                        pass
                    else:
                        key = (size, hash)
                        if key in hashdict:
                            hashdict[key].append((absfilename, 
                                                       self.roots.index(root)))
                        else:
                            hashdict[key] = [(absfilename, 
                                                       self.roots.index(root))]
        return hashdict

    def addFolders(self, *folders):
        self.roots += folders
        self._addHashs(*folders)
        self._renewDerivatives()
        
    def __init__(self, *folders):
        self.roots = ()
        self._hashes = {}
        
        if folders:
            self.addFolders(*folders)
    
    def _splitByIdentity(self, list):
        identity_classes = []
        for f1 in list:
            if not in_list_of_lists(identity_classes, f1):
                for f2 in list[list.index(f1)+1:]:
                    if not in_list_of_lists(identity_classes, f2):
                        if compareFiles(f1[0],f2[0]):
                            idx = in_list_of_lists(identity_classes, f1)
                            if idx:
                                identity_classes[idx-1].append(f2)
                            else:
                                identity_classes.append([f1,f2])  
        return identity_classes
    
    def _checkDuplicates():
        self._duplicates = []
        self._unique = [self._hash_unique[key][0] for key in self._hash_unique]
        
        for key in self._hash_dublicates[key]:
            identity_classes = 
                              self._splitByIdentity(self._hash_dublicates[key])
            self._duplicates = []
            for identity_class in identity_classes:
                if len(identity_class) > 1:
                    self._duplicates.append(identity_class)
                elif len(identity_class) == 1:
                    self._unique += identity_class
                    
    def getUnique(self, *folders):
        if self._unique == None:
            self._checkDuplicates()
        if not folders:
            return tuple(self._unique)   
        else:
            unique = [file for file in self._unique 
                           if self.roots[file[1]] in folders]
            for duplicates_list in self._duplicates:
                for duplicate in duplicates_list:
                    if self.roots[duplicate[1]] not in folders:
                        break
                else:
                    unique += [duplicate[0] for duplicate in duplicates_list]
            return tuple(unique)
    
    def getDuplicates(self, *folders):
        if self._duplicates == None:
            self._checkDuplicates()
        if not folders:
            return tuple(self._duplicates)  
        else:
            duplicates = []
            for duplicates_list in self._duplicates:
                for folder in folders
                    if self.root.index(folder) in \
                               [duplicate[1] for duplicate in duplicates_list]:
                        continue
                    else:
                        break
                else:
                    duplicates.append(tuple(duplicate[0] 
                                             for duplicate in duplicates_list))
            return tuple(duplicates)

def writeDuplicatesToFile(hashdict, filename = 'DuplicatesList.txt'):
    with open(filename, 'wt', encoding="utf8") as fd:
        for hashfile in sorted(hashdict.keys()):
            fd.write(str(hashfile)+':\n')
            for dirname, filename in hashdict[hashfile]:
                fd.write('\t'+dirname+'\\'+filename+'\n')

def getDuplicatesFolders(hashdict):
    dfl = tuple(set((dirname, len(os.listdir(dirname))) for dirname, filename in hashdict[hashfile]) for hashfile in hashdict.keys())
    dfs = { 'folderssets' : [], 'counts' : [] }
    for foldersset in dfl:
        if foldersset in dfs['folderssets']:
            dfs['counts'][dfs['folderssets'].index(foldersset)] += 1
        else:
            dfs['folderssets'].append(foldersset)
            dfs['counts'].append(1)
    dfs = tuple({'foldersset' : foldersset, 'count' : count} for foldersset, count in zip(dfs['folderssets'], dfs['counts']))
    return dfs

def writeFoldersToFile(dfs, filename = 'DuplicatesFolders.txt'):
    with open(filename, 'wt', encoding="utf8") as fd:
        for d in dfs:
            fd.write('[%d]:' % d['count'])
            for folder in d['foldersset']:
                fd.write('\t{0[0]} [{0[1]}]\n'.format(folder))
            fd.write('\n')

if __name__ == '__main__':
    d = getDuplicatesDict()
    writeDuplicatesToFile(d)
    writeFoldersToFile(getDuplicatesFolders(d))