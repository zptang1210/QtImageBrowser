import os
from enum import Enum

PathType = Enum('PathType', ('Server', 'Local', 'Invalid'))

def getPathType(path):
    if path.count(':') == 1:
        # should be a server path, but need some further detect
        srvFullName, actualPath = path.split(':')
        if srvFullName.count('@') == 1:
            return PathType.Server
        else:
            return PathType.Invalid
    else:
        return PathType.Local

def normalizePath(path):
    pathType = getPathType(path)
    if pathType == PathType.Local:
        return os.path.abspath(os.path.normpath(path))
    elif pathType == PathType.Server:
        return path
    else:
        raise ValueError('invalid path as argument.')

def parseServerPath(path):
    if getPathType(path) != PathType.Server:
        raise ValueError('invalid path as argument.')

    srvFullName, actualPath = path.split(':')
    userName, serverName = srvFullName.split('@')

    return userName, serverName, actualPath

def constructServerPath(serverName, userName, serverPath):
    return f'{userName}@{serverName}:{serverPath}'
