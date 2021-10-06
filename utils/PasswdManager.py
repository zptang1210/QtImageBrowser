import getpass
from PyQt5.QtWidgets import QInputDialog, QLineEdit

class PasswdManager:
    def __init__(self):
        self.passwds = {}

    def getPasswd(self, srv): # srv = (serverName, userName)
        passwd = self.passwds.get(srv, None)
        if passwd is not None:
            return passwd

        passwd = PasswdManager.requestPasswd(srv)
        if passwd != '':
            self.passwds[srv] = passwd
        return passwd
    
    def invalidateStoredPasswd(self, srv):
        if srv in self.passwds.keys():
            del self.passwds[srv]

    def requestPasswd(srv):
        srv_str = f'{srv[1]}@{srv[0]}'
        passwd = getpass.getpass(srv_str + '\'s password: ')

        # UI implementation # BUG
        # passwd, ok = QInputDialog.getText(None, "Authentification", "Password:", QLineEdit.Password)

        return passwd


passwdManager = PasswdManager()

