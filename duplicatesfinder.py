#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3.4.3, set console to utf-8 before using

# TODO
#    Fix problem with display unicode filenames in console (force interpreter send to terminal UTF-8, even, if console work with ANSI, 866, etc.)

''' Duplicates finder '''

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
                    
def getDuplicatesDict(path = '.'):
    hashdict = {}
    for dirname, dirslist, filelist in os.walk(path):
        print(dirname)
        for filename in filelist:
            absfilename = dirname+'\\'+filename
            try:
                hash = getHashSum(absfilename)
                size = os.path.getsize(absfilename)
                key = (size, hash)
                if key in hashdict:
                    hashdict[key].append((dirname, filename))
                else:
                    hashdict[key] = [(dirname, filename)]
            except:
                print("ERROR WHILE ACCESS TO FILE:", absfilename)
    print('Walk done')
    for key in list(hashdict.keys()):
        if len(hashdict[key]) == 1:
            del hashdict[key]
    # Compare files with equal hashes byte per byte to make shure that they are same
    for key in list(hashdict.keys()):
        duplicateslists = []
        for i in range (0, len(hashdict[key])): # C-style enabled
            for j in range (i+1, len(hashdict[key])):
                nextj = False
                for dl in duplicateslists:
                    if hashdict[key][j] in dl:
                        nextj = True
                        break
                if nextj: 
                    continue
                if compareFiles('\\'.join(hashdict[key][i]), '\\'.join(hashdict[key][j])):
                    for dl in duplicateslists:
                        if hashdict[key][i] in dl:
                            dl.append(hashdict[key][j])
                            break
                    else:
                        duplicateslists.append([hashdict[key][i], hashdict[key][j]])
        counter = 1
        listscount = len(duplicateslists)
        for dl in duplicateslists:
            hashdict[key+(counter, listscount)] = dl
            counter += 1
        del hashdict[key]
    return hashdict

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