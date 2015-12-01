import os
import sys
import importlib

modulenames = []
for name in os.listdir(sys.path[0]) :
    if (name.endswith('.py') 
                        and os.path.isfile(os.path.join(sys.path[0], name))]):
        modulenames.append(name[:-3])

for modulename in modulenames:
    try:
        __import__(modulename, fromlist = (modulename,))
    except:
        pass
    
def alias(*args):
    pass

def cd(*args):
    pass

def ls(*args):
    pass
    
def show(*args):
    # pie, bar, graph diagrams picking
    pass

def exit(*args):
    continue_ = False