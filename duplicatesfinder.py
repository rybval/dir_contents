#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3.4.3

import os
from hashlib import md5, sha1, sha256, sha512

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
                    
def getHashs(*roots):
    hashdict = {}
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
                        hashdict[key].append((absfilename, root))
                    else:
                        hashdict[key] = [(absfilename, root)]
    return hashdict
    
def checkHashDuplicates(hashdict):
    hashes = {}
    hashes['duplicates'], hashes['unique'] = {}, {}
    for key in hashdict:
        if len(hashdict[key]) > 1:
            hashes['duplicates'][key] = hashdict[key]
        elif len(hashdict[key]) == 1:
            hashes['unique'][key] = hashdict[key]
    return hashes

def in_list_of_lists(ll, item):
    for list in ll:
        if item in list:
            return ll.index(list)+1
    return False
    
def splitByIdentity(list):
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
    
def checkDuplicates(hashdupldict):
    duplicates = {}
    unique = []
    for key in hashdupldict[key]:
        icls = splitByIdentity(hashdupldict[key])
        dcls = []
        for icl in icls:
            if len(icl) > 1:
                dcls.append(icl)
            elif len(icl) == 1:
                unique += icl
        for dcl in dcls:
            duplicates[key+((dcls.index(dcl), len(dcls)),)] = dcl
    return {'duplicates': duplicates, 'unique': unique}
           
def getDuplicates(*folders, hashdict=None):
    if not hashdict:
        hashdict = getHashs(*folders)
    return checkDuplicates(checkHashDuplicates(hashdict)['duplicates'])['duplicates']
    
def getUnique(*folders, hashdict=None):
    if not hashdict:
        hashdict = getHashs(*folders)
    hashes = checkHashDuplicates(hashdict)
    unique = [hashes['unique'][key][0] for key in hashes['unique']]
    unique += checkDuplicates(hashes['duplicates'])['unique']
    return unique
    
def getUnique(folder, *folders):
    folders = (folder,)+folders
    getHashs(*folders)

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