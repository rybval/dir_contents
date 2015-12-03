import os
import sys
import commands
import subprocess

def invitation():
    return '> '

try:
    onstart = open(os.path.join(os.path.expanduser('~'), 'dir_contents', 
                                                         'shell', '.onstart'))
except:
    pass
else:
    for line in onstart:
        process_input(line)
        
def process_input(string):
    comand, *args = string.split()
    if comand in aliases:
        comand = aliases[comand]
        comand, *_args = comand.split()
        args = _args + args
    try:
        comand = getattr(commands, comand)
    except:
        try:
            subprocess.call([comand] + args)
            # Catch output or explore syntax and abilities of func/module
        except:
            print('Error: Command not found', file = sys.stderr)
    else:
        comand(args)

def main_loop():
    global continue_ = True
    while loop:
        string = input(invitation())
        process_input(string)
                