import os

def isServerPath(path):
    return path.count(':') == 1

def normalizePath(path):
    if not isServerPath(path):
        return os.path.abspath(os.path.normpath(path))
    else:
        return path