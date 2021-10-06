import json

class RemoteServerManager:

    def __init__(self):
        with open('./configs/serverConfigs/registeredServerConfigs.json', 'r') as fin:
            self.configs_json = json.load(fin)
        
        # read and check configs_json
        try:
            self.servers = {}
            for item in self.configs_json['config_files']:
                name, path = item['name'], item['file']
                with open(path, 'r') as fin:
                    config = json.load(fin)
                
                assert {"server", "username", "auth_method", "processor_path", "template_path"}.issubset(set(config.keys()))
                assert (config['processor_path'] is None and config['template_path'] is None) or (config['processor_path'] is not None and config['template_path'] is not None)
                allowProcessing = False if config['processor_path'] is None else True

                self.servers[name] = {'config': config, 'path': path, 'allowProcessing': allowProcessing}
        except Exception as e:
            print('Error occurs when loading server configurations...')
            raise e
            
    def getListOfServers(self):
        return list(self.servers.keys())

    def getListOfServersAllowingProcessing(self):
        nameList = []
        for name in self.servers.keys():
            if self.servers[name]['allowProcessing']:
                nameList.append(name)
        
        return nameList

    def getServerAddr(self, serverName):
        if serverName in self.servers.keys():
            return self.servers[serverName]['config']['username'] + '@' + self.servers[serverName]['config']['server']
        else:
            raise ValueError('invalid server name.')

    def getConfig(self, serverName):
        if serverName in self.servers.keys():
            return self.servers[serverName]['config']
        else:
            raise ValueError('invalid server name.')



remoteServerManager = RemoteServerManager()



if __name__ == "__main__":
    print(remoteServerManager.getListOfServersAllowingProcessing())
    print(remoteServerManager.getListOfServers())