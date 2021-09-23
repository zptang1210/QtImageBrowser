import os

def isServerPath(path):
    return ':' in path #TODO: a more comprehensive check

def normalizePath(path):
    if not isServerPath(path):
        return os.path.abspath(os.path.normpath(path))
    else:
        return path # TODO