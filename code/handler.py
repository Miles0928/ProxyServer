# -*- coding: utf-8 -*-

import os, json, queue
import socket, select, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from config import Config

config = Config()


import logging
logfile = config.proxyLog
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
logging.basicConfig(filename=logfile, level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)


class ProxyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = directory
        self.block_list, self.proxy_list = config.loadHost()
        self.maxbuffer = 10*1024                ## 10K
        self.do_SETUP()
        super().__init__(*args, **kwargs)
    
    def do_SETUP(self):
        self.do_GET = self.do_METHOD
        self.do_POST = self.do_METHOD
        self.do_HEAD = self.do_METHOD
        self.do_PUT = self.do_METHOD
        self.do_DELETE = self.do_METHOD
        self.do_OPTIONS = self.do_METHOD
        
    def do_CONNECT(self):
        self.TLS = True
        self.handle_host()
        
    def do_METHOD(self):
        self.TLS = False
        self.handle_host()
        
    def handle_host(self):
        self.Host = self.headers.get('Host', '')
        host, _, port = self.Host.rpartition(':')
        try:
            port = int(port)
        except:
            host, port = self.Host, 443 if self.TLS else 80
        
        if host in self.block_list:
            logging.info('[Block] {} {}'.format(host, port))
            return self.do_BLOCK()
        elif host in self.proxy_list:
            logging.info('[Forward] {} {}'.format(host, port))
            return self.do_FORWARD()
        else:
            logging.info('[Direct] {} {}'.format(host, port))
            return self.do_PROXY(host, port)
            
    def do_PROXY(self, host, port):
        try:
            host_ip = socket.getaddrinfo(host, port, socket.AF_INET6)[0][-1][0]
            server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        except:
            try:
                host_ip = socket.getaddrinfo(host, port, socket.AF_INET)[0][-1][0]
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except:
                logging.info('[D2F] {} {}'.format(host, port))
                return self.do_FORWARD()

        client_socket = self.connection
        
        if self.TLS:
            try:
                server_socket.connect_ex((host_ip, port))
                client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self.bi_forward(client_socket, server_socket)
            except:
                client_socket.send(b'HTTP/1.1 501 Connection Error\r\n\r\n')
                server_socket.close()
                client_socket.close()
        else:
            del self.headers['Proxy-Connection']
            self.headers['Connection'] = 'close'
            
            raw_data = self.handle_headers(False)
            
            try:
                server_socket.connect_ex((host_ip, port))
                server_socket.sendall(raw_data)
                self.forward(server_socket, client_socket)
            except:
                server_socket.close()
                client_socket.send(b'HTTP/1.1 501 Connection Error\r\n\r\n')
            finally:
                client_socket.close()
                
    def do_FORWARD(self):
        self.maxbuffer = 20*1024                ## 20K
        # client_socket = self.request
        client_socket = self.connection
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect_ex(('localhost', 8087))
        
        raw_headers = self.handle_headers(True)
        server_socket.sendall(self.raw_requestline + raw_headers)
        
        if self.TLS:
            self.bi_forward(client_socket, server_socket)
        else:
            self.forward(client_socket, server_socket)
    
    def do_BLOCK(self):
        local_socket = self.connection
        if self.TLS:
            ## showing a customized web
            local_socket.send(b'HTTP/1.1 501 Connection Error\r\n\r\n')
        else:
            local_socket.send(b'HTTP/1.1 501 Connection Error\r\n\r\n')
        local_socket.close()
        
    
    def handle_headers(self, method=True)
        headers = ["{key}: {value}\r\n".format(key=key, value=value) for key, value in self.headers.items()]
        raw_headers = ''.join(headers).encode() + b'\r\n'
        
        if method:          ## FORWARD
            return raw_headers
        else:               ## PROXY
            raw_path = self.path.rpartition(self.Host)[-1]
            raw_headers_path = ' '.join([self.command, raw_path, self.request_version]).encode()
            raw_headers_path += b'\r\n'

            raw_bytes_data = b''
            if self.command in ('POST', 'PUT'):
                raw_bytes_data = self.read_data()
            raw_data = raw_headers_path + raw_headers + raw_bytes_data
            return raw_data
    
    # two-way forward data
    # how to control socket close at correct time
    def bi_forward(self, client, server):
        fdset = [client, server]
        
        while True:
            r, w, e = select.select(fdset, [], [])

            if client in r:
                raw_data = client.recv(self.maxbuffer)
                if not raw_data:
                    break
                server.sendall(raw_data)
                
            if server in r:
                raw_data = server.recv(self.maxbuffer)
                if not raw_data:
                    break
                client.sendall(raw_data)
        
        client.close()       
        server.close()


    # one-way forward data
    def forward(self, client, server):
        while True:
            raw_data = client.recv(self.maxbuffer)
            if not raw_data:
                break
            server.sendall(raw_data)
        
        client.close()
        server.close()
            
        
    def read_data(self):
        raw_bytes = b''
        if 'Content-Length' in self.headers:
            try:
                bytes_len = int(self.headers.get('Content-Length', 0))
                raw_bytes = self.rfile.read(bytes_len)
            except:
                pass
                #logging.warning("handle_method_urlfetch read payload failed.")
        elif 'Transfer-Encoding' in self.headers:
            while True:
                chunk_str = self.rfile.readline(65537)
                chunk_list = chunk_str.split(";")
                chunk = int("0x" + chunk_list[0], 0)
                if chunk == 0:
                    break
                raw_bytes += self.rfile.read(chunk)
        return raw_bytes
        

class ForwardHandler(ProxyHandler):
    def handle_host(self):
        self.Host = self.headers.get('Host', '')
        host, _, port = self.Host.rpartition(':')
        try:
            port = int(port)
        except:
            host, port = self.Host, 443 if self.TLS else 80
        
        if host in self.block_list:
            logging.info('[Block] {} {}'.format(host, port))
            return self.do_BLOCK()
        else:
            logging.info('[Forward] {} {}'.format(host, port))
            return self.do_FORWARD()


class ProxyServer():
    def __init__(self, methods=[True, True]):
        self.Q = queue.Queue()
        self.methods = methods
        self.Handler = [ProxyHandler, ForwardHandler]
        host_config = config.getConfig()
        self.Host = host_config[0]
        self.Port = host_config[1:]

    def Proxy(self, Port, ProxyMethod):
        with ThreadingHTTPServer((self.Host, Port), ProxyMethod) as httpd:
            self.Q.put(httpd)
            httpd.serve_forever()

    def start(self):
        thread_list = []
        for index in range(len(self.methods)):
            if self.methods[index]:
                thread = threading.Thread(target=self.Proxy, args=(self.Port[index], self.Handler[index]))
                thread.start()
                thread_list.append(thread)
            else:
                pass

        for var_thread in thread_list:
            var_thread.join()
        

    def stop(self):
        while not self.Q.empty():
            self.Q.get().shutdown()

if __name__ == '__main__':
    ProxyServer().start()
