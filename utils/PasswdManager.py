import getpass
from PyQt5.QtWidgets import QInputDialog, QLineEdit

class PasswdManager:
    def __init__(self):
        self.passwd = None

    def getPass(self):
        if self.passwd is None:
            # getpass implementation
            self.passwd = getpass.getpass()
            ok = True

            # UI implementation # BUG
            # self.passwd, ok = QInputDialog.getText(None, "Authentification", "Password:", QLineEdit.Password)
            if ok: 
                return self.passwd
            else: return ''
        else:
            return self.passwd

    def currentPasswdIsInvalid(self):
        self.passwd = None

passwdManager = PasswdManager()

