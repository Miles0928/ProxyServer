# -*- coding: utf-8 -*-

import os, json

class Config():
    def __init__(self):
        self.directory = os.getcwd()
        self.dataPath = os.path.join(os.path.dirname(self.directory), 'data')
        self.configFile = os.path.join(self.dataPath, 'config.json')
        self.hostFile = os.path.join(self.dataPath, 'host.json')
        self.blockFile = os.path.join(self.dataPath, 'blocklist.txt')
        self.proxyFile = os.path.join(self.dataPath, 'proxylist.txt')
        self.proxyLog = os.path.join(self.dataPath, 'proxy.log')
        os.makedirs(self.dataPath, exist_ok=True)

    def getConfig(self):
        try:
            with open(self.configFile, 'r+') as fd:
                config_info = json.load(fd)
            host = config_info['host']
            port_proxy = config_info['port_proxy']
            port_forward = config_info['port_forward']
        except:
            host = ''
            port_proxy = 8000
            port_forward = 8001
        finally:
            return host, port_proxy, port_forward
    
    def saveConfig(self, host, port_proxy, port_forward):
        config_info = {}
        config_info['host'] = host
        config_info['port_proxy'] = int(port_proxy)
        config_info['port_forward'] = int(port_forward)
        with open(self.configFile, 'w+') as fd:
            json.dump(config_info, fd, indent=4)
            
    def loadHost(self):
        try:
            with open(self.hostFile, 'r+') as fd:
                hosts = json.load(fd)
            with open(self.blockFile, 'r+') as fd:
                block_list = fd.readlines()
                block_list = [host[:-1] if '\n' in host else host for host in block_list]
            with open(self.proxyFile, 'r+') as fd:
                proxy_list = fd.readlines()
                proxy_list = [host[:-1] if '\n' in host else host for host in proxy_list]
        except:
            hosts = {}
            block_list = []
            proxy_list = []
        finally:
            return hosts, block_list, proxy_list
            
    def saveHost(self, host, type=True):
        if type:
            with open(self.blockFile, 'a+') as fd:
                fd.write(host)
                fd.write('\n')
        else:
            with open(self.proxy_list, 'a+') as fd:
                fd.write(host)
                fd.write('\n')
