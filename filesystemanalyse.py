import os
import matplotlib
import matplotlib.pyplot as plt
from colors import neon

def findUnaccessiblePaths(path):
    fails = []
    for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                try:
                    os.path.getsize(fullpath)
                except:
                    defects.append(fullpath)
    return tuple(fails)
    
def findEmptyFolders(path):
    list = []
    for dirname, dirslist, fileslist in os.walk(path):
        if len(dirslist) + len(fileslist) == 0:
            list.append(dirname)
    return tuple(list)

def getFolderSize(path, mode='bytes'):
    if mode not in ('bytes', 'files', 'dirs', 'folders', 'objects'):
        raise ValueError(mode)
        
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        if mode in ('bytes', 'files', 'objects'):
            for filename in filenames:
                if mode == 'bytes':
                    fullpath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(fullpath)
                    except:
                        pass
                elif mode in ('files', 'objects'):
                    total += 1
        if mode in ('dirs', 'folders', 'objects'):
            for dirname in dirnames:
                    total+=1
                
    return total
    
def getObjectSize(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        return getFolderSize(path)
    else:
        raise ValueError
    
def getListSize(paths_iterable):
    paths_iterable = sorted(paths_iterable, key = len)
    
    for path in paths_iterable:
        i = paths_iterable.index(path)+1
        while i < len(paths_iterable):
            if paths_iterable[i].startswith(path):
                del paths_iterable[i]
            else:
                i += 1
            
    total = 0
    for path in paths_iterable:
        total += getObjectSize(path)
    return total

def getSpaceUsage(path, consider_files=False, consider_folders=True):
    items = {}
    rootsize = 0
    for name in os.listdir(path):
        fullpath = os.path.join(path, name)
        if os.path.isdir(fullpath):
            if consider_folders:
                itemname = os.path.join(name,'')
                items[itemname] = getFolderSize(fullpath)
        elif os.path.isfile(fullpath):
            filesize = os.path.getsize(fullpath)
            if consider_files:
                items[name] = filesize
            else: 
                rootsize += filesize
                
    if not consider_files:
        items['[root]'] = rootsize
        
    return items

def sizeConversion(size_in_bytes):
    steps = ('B', 'KB', 'MB', 'GB', 'TB')
    um = 'B'
    for i in range(0, len(steps)-1):
        if size_in_bytes > 2**(i*10):
            um = steps[i]
        else:
            break
    return (size_in_bytes/2**(steps.index(um)*10), um)

def getSizeStr(size_in_bytes):
    return '{0:.2f}{1}'.format(*sizeConversion(size_in_bytes))

def make_autopct(total):
    def my_autopct(pct):
        return '{:.2f}% ({})'.format(pct, getSizeStr(total/100*pct))
    return my_autopct
    
def showMemUsagePieChart(dict, min_wedge_pct=None, 
                         display_other=False, max_mem=None):
    tuples = sorted(dict.items(), key = (lambda item: -item[1]))
    sizes = [item[1] for item in tuples]
    labels = [item[0] for item in tuples]
    total_used = sum(sizes)
    
    if max_mem:
        total = max_mem
    else:
        total = total_used
    
    if min_wedge_pct:
        other_sizes = []
        other_labels = []
        min_absolute_size = (total/100.0) * min_wedge_pct
        for size in sizes:
            if size < min_absolute_size:
                idx = sizes.index(size)
                sizes, other_sizes = sizes[:idx], sizes[idx:]
                labels, other_labels = labels[:idx], labels[idx:]
                sizes.append(sum(other_sizes))
                labels.append('[other]')
                break
    
    if max_mem:
        sizes.append(max_mem-total_used)
        labels.append('[free]')
    
    plt.pie(sizes, labels=labels, colors=neon, startangle=90, 
                                                autopct = make_autopct(total))
    plt.axis('equal')

    plt.show()