#!/usr/bin/env python3
import os
import filesystemanalyse
with open('emptyfolderslist.txt', 'wt', encoding="utf8") as file:
    for dirname in filesystemanalyse.findEmptyFolders():
            file.write(dirname + '\n')