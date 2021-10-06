import pexpect
from pexpect.exceptions import TIMEOUT, EOF
from utils.PasswdManager import passwdManager
from utils.RemoteServerManager import remoteServerManager
from utils.pathUtils import PathType, getPathType, parseServerPath

def rsync(srcPath, destPath):
    # check which is server path and which is local path
    if getPathType(srcPath) == PathType.Invalid or getPathType(destPath) == PathType.Invalid:
        raise ValueError('invalid srcPath or destPath.')

    serverPath = None
    if getPathType(srcPath) == PathType.Server:
        if getPathType(destPath) == PathType.Server: serverPath = None
        else: serverPath = srcPath
    else:
        if getPathType(destPath) == PathType.Server: serverPath = destPath
        else: serverPath = None
    
    if serverPath is None: raise ValueError('srcPath and destPath cannot both be remote or local.')
    userName, serverName, _ = parseServerPath(serverPath)
    passwd = passwdManager.getPasswd((serverName, userName))

    # interact with rsync
    cmd = f'rsync -a --delete {srcPath} {destPath}'  #rsync -av --delete xxx@gypsum.cs.umass.edu:~/testData /Users/xxx/Desktop/tmp
    print('rsync cmd: ', cmd)
    child = pexpect.spawn(cmd)
    
    i = child.expect(["password", EOF, TIMEOUT], timeout=30)
    # print(i, child.before, child.after)
    if i != 0:
        print('Unexpected situation')
        return False

    child.sendline(passwd)
    i = child.expect(["Permission denied", '[Ff]ailed', '[Ee]rror', EOF, TIMEOUT], timeout=200)
    # print(i, child.before, child.after)
    if i == 0:
        print('rsync Permission denied')
        passwdManager.invalidateStoredPasswd((serverName, userName))
        return False
    elif i == 3:
        print('rsync Ok')
        return True
    elif i == 4:
        print('rsync Timeout')
        return False
    else:
        print('rsync Error')
        return False