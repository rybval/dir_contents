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
    
def splitByIdentity(list, compareCallBack):
    identity_classes = []
    for item_1 in list:
        if not in_list_of_lists(identity_classes, item_1):
            for item_2 in list[list.index(item_1)+1:]:
                if not in_list_of_lists(identity_classes, item_2):
                    if compareCallBack(item_1, item_2):
                        idx = in_list_of_lists(identity_classes, item_1)
                        if idx:
                            identity_classes[idx-1].append(item_2)
                        else:
                            identity_classes.append([item_1, item_2])  
    return identity_classes

def_chunksize = 2**9*2**10 #512KB — standart sector size
    
def getHashSum(fileName, hashfunc = md5, chunksize = def_chunksize):
    h = hashfunc()
    with open(fileName, 'rb') as fd:
        while True:
            chunk = fd.read(chunksize)
            if chunk:
                h.update(chunk)
            else:
                return h.hexdigest()
                
def pathIncapsulation(paths_iterable):
    paths_iterable = sorted(paths_iterable, key = len)
    for path in paths_iterable:
        i = paths_iterable.index(path)+1
        while i < len(paths_iterable):
            if paths_iterable[i].startswith(os.path.join(path, '')) \
                                                  or paths_iterable[i] == path:
                del paths_iterable[i]
            else:
                i += 1
    return tuple(paths_iterable)
    
def isStartsWith(path, prefix, *prefixes):
    prefixes = (prefix,) + prefixes
    prefixes = tuple(os.path.join(p, '') for p in prefixes)
    for prefix in prefixes:
        if path.startswith(prefix):
            return True
    else:
        return False
                 
def compareFiles(filename_1, filename_2, chunksize = def_chunksize):
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
        
    def _already_processed(self, path):
        for key in self._hashes:
            for file in self._hashes[key]:
                if file.startswith(path):
                    return True
        else:
            return False

    def addFolders(self, folder, *folders):
        folders = pathIncapsulation((folder,) + folders)
        changed = False
        for folder in folders:
            for dirname, dirslist, filelist in os.walk(folder):
                if not self._already_processed(dirname):
                    changed = True
                    for filename in filelist:
                        absfilename = os.path.join(dirname, filename)
                        try:
                            hash = getHashSum(absfilename)
                            size = os.path.getsize(absfilename)
                        except:
                            pass
                        else:
                            #DEBAG FEACHURE# print(absfilename)
                            key = (size, hash)
                            if key in self._hashes:
                                self._hashes[key].append(absfilename)
                            else:
                                self._hashes[key] = [absfilename]
        if changed:
            self._renewDerivatives()
        
    def excludeFolders(self, folder, *folders):
        folders = pathIncapsulation((folder,) + folders)
        changed = False
        for folder in folders:
            folder = os.path.join(folder, '')
            for key in self._hashes:
                to_del = []
                for file in self._hashes[key]:
                    if file.startswith(folder):
                        to_del.append(file)
                if to_del:
                    changed = True
                    for file in to_del:
                        self._hashes[key].remove(file)
        if changed:
            self._renewDerivatives()
        
    def __init__(self, *folders):
        self._hashes = {}
        
        if folders:
            self.addFolders(*folders)
    
    def _checkDuplicates(self):
        self._duplicates = []
        self._unique = [self._hash_unique[key][0] for key in self._hash_unique]
        
        for key in self._hash_dublicates:
            identity_classes = \
                splitByIdentity(self._hash_dublicates[key], compareFiles)
            for identity_class in identity_classes:
                if len(identity_class) > 1:
                    self._duplicates.append(identity_class)
                elif len(identity_class) == 1:
                    self._unique += identity_class
    
    def getUnique(self, *folders, mode = 'absolute'):
        """ 
        Returns tuple of se with dublicates.
        If no folders given returns all absolute unique files,
            argument 'mode' ignored.
        Else returns only files, contained in folders:
            if mode is absolute: 
                returns only files, which have no duplicates
            elif mode is outside:
                returns files, which have no dublicates outside the folders
            elif mode is inside:
                returns files, which have no dublicates inside
        """
        if self._unique == None:
            self._checkDuplicates()
        if not folders:
            return tuple(self._unique)   
        else:
            unique = []
            for file in self._unique:
                if isStartsWith(file, *folders):
                    unique.append(file)
            if mode != 'absolute':
                for duplicates_list in self._duplicates:
                    inside = []
                    for file in duplicates_list:
                        if mode == 'outside':
                            if not isStartsWith(file, *folders):
                                break
                        elif mode == 'inside':
                            if isStartsWith(file, *folders):
                                inside.append(file)
                                if len(inside) >= 2:
                                    break
                    else:
                        if mode == 'outside':
                            unique += duplicates_list
                        elif mode == 'inside' and len(inside) == 1:
                            unique += inside
            return tuple(unique)
    
    def getDuplicates(self, *folders, mode = 'inner-'):
        """ 
        Returns tuple of tuples with dublicates.
        If no folders given returns all dublicates, argument 'mode' ignored.
        Else
            if mode starts with 'all':
                returns all files, which duplicates contains
                in all folders given at the same time
            elif mode starts with 'any':
                returns all files, which a duplicates of any processed files
            elif mode starts witn 'inner': 
                returns all files, which duplicated in the folders given
            if mode ends with '-':
                returns only duplicates, which contains in folders given
            elif mode ends with '+':
                for finded files returns all their duplicates
        """
        if self._duplicates == None:
            self._checkDuplicates()
        if not folders:     
            return  tuple(tuple(duplicates_list) \
                                    for duplicates_list in self._duplicates)
        else:
            duplicates = []
            for duplicates_list in self._duplicates:
                current_duplicates = []
                for duplicate in duplicates_list:
                    if isStartsWith(duplicate, *folders):
                        current_duplicates.append(duplicate)
                if mode.startswith('all'):
                    for folder in folders:
                        for p in current_duplicates:
                            if isStartsWith(p, folder):
                                break
                        else:
                            break
                    else:
                        if mode[-1] == '-':
                            duplicates.append(tuple(current_duplicates))
                        elif mode[-1] == '+':
                            duplicates.append(tuple(duplicates_list))
                elif mode.startswith('inner'):
                    if len(current_duplicates) >= 2:
                        if mode[-1] == '-':
                            duplicates.append(tuple(current_duplicates))
                        elif mode[-1] == '+':
                            duplicates.append(tuple(duplicates_list))
                elif mode.startswith('any'):
                    if mode[-1] == '-':
                        duplicates.append(tuple(current_duplicates))
                    elif mode[-1] == '+':
                        duplicates.append(tuple(duplicates_list))
            return tuple(duplicates)
     
        #elif len(folders) == 1:
        #    duplicates = []
        #    folder = os.path.join(folders[0], '')
        #    for duplicates_list in self._duplicates:
        #        current_duplicates = []
        #        for duplicate in duplicates_list:
        #            if duplicate.startswith(folder):
                        # if mode == 'foreign+':
                            # current_duplicates = duplicates_list
                            # break
                        # else:
                            # current_duplicates.append(duplicate)
                # if current_duplicates:
                    # if mode == 'any+':
                        # duplicates += current_duplicates
                    # elif mode == 'any-':
                        # duplicates += current_duplicates
                    # elif mode == 'only+':
                        # if len(current_duplicates) >= 2:
                            # duplicates += duplicates_list
                    # elif mode == 'only-':
                        # if len(current_duplicates) >= 2:
                            # duplicates += current_duplicates
            # return tuple(duplicates)

    def getDuplicatesOfFile(path):
        pass
'''
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
'''