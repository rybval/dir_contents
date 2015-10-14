#!/usr/bin/env python3
import os
with open('emptyfolderslist.txt', 'wt', encoding="utf8") as file:
    for dirname, dirslist, fileslist in os.walk('.'):
        if len(dirslist) + len(fileslist) == 0:
            file.write(dirname + '\n')