import pexpect
from pexpect.exceptions import TIMEOUT, EOF
import utils.PasswdManager as PasswdManager

def rsync(cmd):
    print('rsync cmd: ', cmd)
    child = pexpect.spawn(cmd)
    
    i = child.expect(["password", EOF, TIMEOUT], timeout=30)
    # print(i, child.before, child.after)
    if i != 0:
        print('Unexpected situation')
        return False

    passwd = PasswdManager.passwdManager.getPass()
    child.sendline(passwd)
    i = child.expect(["Permission denied", 'failed', 'error', EOF, TIMEOUT], timeout=200)
    # print(i, child.before, child.after)
    if i == 0:
        print('rsync Permission denied')
        PasswdManager.passwdManager.currentPasswdIsInvalid()
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