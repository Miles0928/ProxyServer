# -*- coding: utf-8 -*-

import os, json

class Config():
    def __init__(self):
        self.directory = os.getcwd()
        self.configFile = os.path.join(self.directory, 'data', 'config.json')
        self.hostFile = os.path.join(self.directory, 'data', 'hostlist.json')
        os.makedirs(os.path.dirname(self.configFile), exist_ok=True)

    def getConfig(self):
        try:
            with open(self.configFile, 'r+') as fd:
                config_info = json.load(fd)
            host = config_info['Host']
            port = config_info['Port']
        except:
            host = ''
            port = 8080
            config_info = {
                'Host': host,
                'Port': port,
                }
            self.saveConfig(**config_info)
        finally:
            return host, port
    
    def saveConfig(self, **Host):
        try:
            with open(self.configFile, 'r+') as fd:
                config_info = json.load(fd)
                config_info.update(Host)
        except:
            config_info = Host
        finally:    
            with open(self.configFile, 'w+') as fd:
                json.dump(config_info, fd, indent=4)
            
    def loadHost(self):
        try:
            with open(self.hostFile, 'r+') as fd:
                hostlist = json.load(fd)
            proxy_list = hostlist.get('Proxy', [])
            block_list = hostlist.get('Block', [])
        except:
            proxy_list = []
            block_list = []
            hostlist = {'Proxy': [], 'Block': []}
            with open(self.hostFile, 'w+') as fd:
                json.dump(hostlist, fd, indent=4)
        finally:
            return proxy_list, block_list
     
    def saveHost(self, Host, method=True):
        try:
            with open(self.hostFile, 'r+') as fd:
                hostlist = json.load(fd)
        except:
            hostlist = {'Proxy': [], 'Block': []}
        finally:
            for key in Host.keys():
                ## Proxy host
                if method:
                    hostlist.get(key).append(Host.get(key))
                ## Block host
                else:
                    hostlist.get(key).remove(Host.get(key))
            
            hostlist[key] = list(set(hostlist.get(key)))
            
            with open(self.hostFile, 'w+') as fd:
                json.dump(hostlist, fd, indent=4)