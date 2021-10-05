import json
import traceback
import utils.PasswdManager as PasswdManager
from pexpect import pxssh

class RemoteServer:
    def __init__(self, configFile):
        self.config = None
        self.script = None
        self.server = None
        self.connected = False

        with open(configFile, 'r') as fin:
            self.config = json.load(fin)
        
        with open(self.config['template_path'], 'r') as fin:
            self.script = fin.readlines()

    def login(self):
        try:
            self.server = pxssh.pxssh()
            self.server.login(server=self.config['server'], username=self.config['username'], password=PasswdManager.passwdManager.getPass(), sync_multiplier=5)
        except pxssh.ExceptionPexpect as e:
            print('pxssh failed.', e)
            PasswdManager.passwdManager.currentPasswdIsInvalid()
            self.connected = False
            return False
        else:
            self.connected = True
            return True

    def logout(self):
        try:
            if self.server is not None and self.connected:
                self.server.logout()
        except:
            print('pxssh logout failed.')
            return False
        else:
            print('pxssh logout succeeded.')
            self.connected = False
            return True

    def runTemplateScript(self, replace, expectRe, timeout=500):
        if self.script is None or self.connected == False or self.server is None:
            print('failed the initial check for script run.')
            return None

        try:
            for line in self.script:
                line = line.strip()
                if line == '[RUN]':
                    line = replace['[RUN]']
                    keyLine = True
                elif line in replace.keys():
                    line = replace[line]
                    keyLine = False
                else:
                    keyLine = False

                print('cmd sent:', line)
                
                self.server.sendline(line)
                if not keyLine:
                    self.server.prompt(timeout=(timeout//2))
                else:
                    self.server.expect(expectRe, timeout=timeout)
                    result = self.server.after.decode()
                # print('debug info:', self.server.before, self.server.after)
        except Exception as e:
            print('error occurs during running the script')
            print(e, '\n', traceback.format_exc())
            return None
        else:
            return result

    def __del__(self):
        self.logout()

    def get_server(self):
        if self.config is not None:
            return self.config['server']
        else:
            return None

    def get_username(self):
        if self.config is not None:
            return self.config['username']
        else:
            return None

    def get_processor_path(self):
        if self.config is not None:
            return self.config['processor_path']
        else:
            return None

    def get_template_path(self):
        if self.config is not None:
            return self.config['template_path']
        else:
            return None


if __name__ == '__main__':
    server = RemoteServer('./configs/serverConfigs/mygypsum.json')
    print(server.login())