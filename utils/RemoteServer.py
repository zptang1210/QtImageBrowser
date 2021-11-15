import json
from utils.PasswdManager import passwdManager
from pexpect import pxssh

class RemoteServer:

    TIMEOUT = 240

    def __init__(self, config):
        self.config = None
        self.script = None
        self.server = None
        self.connected = False

        self.config = config
        
        try:
            with open(self.config['template_path'], 'r') as fin:
                self.script = fin.readlines()
        except:
            print('loading template file failed.')
            self.script = None

    def login(self):
        print('pxssh is trying to log into the server.')
        try:
            self.server = pxssh.pxssh()
            # self.server.force_password = True # TODO: support password login only for now
            if self.config['auth_method'] == 'password':
                passwd = passwdManager.getPasswd((self.config['server'], self.config['username']))
                self.server.login(server=self.config['server'], username=self.config['username'], password=passwd, sync_multiplier=5)
            else:
                privateKeyPath = self.config['key_file']
                self.server.login(server=self.config['server'], username=self.config['username'], ssh_key=privateKeyPath, sync_multiplier=5)
        except pxssh.ExceptionPexpect as e:
            print('pxssh failed.', e)
            passwdManager.invalidateStoredPasswd((self.config['server'], self.config['username']))
            self.server = None
            self.connected = False
            return False
        else:
            self.connected = True
            return True

    def logout(self):
        print('pxssh is trying to logout from the server.')
        try:
            if self.server is not None and self.connected:
                self.server.logout()
        except:
            print('pxssh logout failed.')
            flag = False
        else:
            print('pxssh logout succeeded.')
            flag = True

        self.server = None
        self.connected = False
        return flag

    def runTemplateScript(self, replace, expectRe, timeout=TIMEOUT):
        if self.script is None or self.connected == False or self.server is None:
            print('failed the initial check before running the script.')
            return None

        result = None
        for line in self.script:
            self.server.set_unique_prompt()
            try:
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
                    self.server.prompt(timeout=timeout)
                else:
                    i = self.server.expect([expectRe, '[Ee]rror', '[Ff]ailed', '[Ee]xception'], timeout=timeout)
                    if i != 0:
                        print('debug info:', self.server.before, self.server.after)
                        raise RuntimeError('failed to run [RUN].')
                    else:
                        result = self.server.after.decode()

                # print('debug info:', self.server.before, self.server.after)
            except Exception as e:
                print('error occurs during running the command: ', line, e)

        if result is None:
            print('running the script failed')
            return None
        else:
            return result

    def __del__(self):
        if self.server is not None and self.connected:
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
    with open('./configs/serverConfigs/mygypsum.json', 'r') as fin:
        config = json.load(fin)

    server = RemoteServer(config)
    print(server.login())