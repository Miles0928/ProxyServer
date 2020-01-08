# -*- coding: utf-8 -*-

import os, json, queue
import socket, select, threading, socks
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from config import Config

config = Config()
Host, Port, Socks = config.getConfig()

class Proxy(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.maxbuffer = 2*1024        # 2K
        # self.Socks = Socks
        self.Socks = config.getConfig()[-1]
        self.sock_args = {'Family': socket.AF_INET,'Type': socket.SOCK_STREAM}
        self.sock_args_v6 = {'Family': socket.AF_INET6,'Type': socket.SOCK_STREAM}
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
        self.handle_Host()
        
    def do_METHOD(self):
        self.TLS = False
        self.handle_Host()
    
    def do_PROXY(self, method=True):
        # self.Host >>-- (host, port)
        # self.Sock_args >>-- (AF_INET[6], SOCK_STREAM)
        self.maxbuffer = self.maxbuffer*2
        client_socket = self.request
        
        if method:
            try:
                server_socket = socket.socket(*self.Sock_args_v6)
                server_socket.connect(self.Host)
            except:
                server_socket = socket.socket(*self.Sock_args)
                server_socket.connect_ex(self.Host)
        else:
            try:
                server_socket = socket.socket(*self.Sock_args)
                server_socket.connect(self.Host)
            except:
                server_socket = socket.socket(*self.Sock_args_v6)
                server_socket.connect_ex(self.Host)
        
        self.Host_in = client_socket.getpeername()[0]
        self.Host_out = server_socket.getsockname()[0]
        # print('Proxy: {} {} [ {} -->> {} ]'.format(*self.Host, self.Host_in, self.Host_out))
        
        if self.TLS:
            try:
                client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self.bi_forward(client_socket, server_socket)
            except:
                # client_socket.sendall(b'HTTP/1.1 501 Connection Error\r\n\r\n')
                server_socket.close()
                client_socket.close()
        else:
            del self.headers['Proxy-Connection']
            self.headers['Connection'] = 'close'
            
            raw_data = self.handle_headers(False)
            
            try:
                server_socket.sendall(raw_data)
                self.forward(server_socket, client_socket)
            except:
                server_socket.close()
                # client_socket.send(b'HTTP/1.1 501 Connection Error\r\n\r\n')
            finally:
                pass

    def do_VPN(self):
        self.maxbuffer = self.maxbuffer*2
        Host_proxy = ('192.168.10.1', self.Socks)
        
        client_socket = self.request
        server_socket = socks.socksocket()
        server_socket.set_proxy(socks.SOCKS5, *Host_proxy)
        
        server_socket.connect(self.Host)
        
        self.Host_in = client_socket.getpeername()[0]
        self.Host_out = server_socket.getsockname()[0]
        # print('VPN: {} {} [ {} -->> {} ]'.format(*self.Host, self.Host_in, self.Host_out))
        
        
        if self.TLS:
            try:
                client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self.bi_forward(client_socket, server_socket)
            except:
                # client_socket.sendall(b'HTTP/1.1 501 Connection Error\r\n\r\n')
                server_socket.close()
                client_socket.close()
        else:
            try:                
                raw_headers = self.handle_headers(True)
                server_socket.sendall(self.raw_requestline + raw_headers)

                self.forward(server_socket, client_socket)
            except:
                pass
    
    def do_BLOCK(self):
        client_socket = self.request
        
        self.Host_in = client_socket.getpeername()[0]
        self.Host_out = None
        # print('Block: {} {} [ {} -->> {} ]'.format(*self.Host, self.Host_in, self.Host_out))
        
        if self.TLS:
            client_socket.sendall(b'HTTP/1.1 501 Connection Error\r\n\r\n')
        else:
            client_socket.sendall(b'HTTP/1.1 501 Connection Error\r\n\r\n')
        client_socket.close()

    def handle_Host(self):
        pass

    def handle_headers(self, method=True):
        headers = ["{key}: {value}\r\n".format(key=key, value=value) for key, value in self.headers.items()]
        raw_headers = ''.join(headers).encode() + b'\r\n'
        
        if method:          ## FORWARD
            return raw_headers
        else:               ## PROXY
            Host_init = self.headers.get('Host', '')
            raw_path = self.path.rpartition(Host_init)[-1]
            raw_headers_path = ' '.join([self.command, raw_path, self.request_version]).encode()
            raw_headers_path += b'\r\n'

            raw_bytes_data = b''
            if self.command in ('POST', 'PUT'):
                raw_bytes_data = self.read_data()
            raw_data = raw_headers_path + raw_headers + raw_bytes_data
            # if self.command in ('POST', 'PUT'):
                # print(raw_data)
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
                
        elif 'Transfer-Encoding' in self.headers:
            while True:
                chunk_str = self.rfile.readline(65537)
                chunk_list = chunk_str.split(";")
                chunk = int("0x" + chunk_list[0], 0)
                if chunk == 0:
                    break
                raw_bytes += self.rfile.read(chunk)
        return raw_bytes


class ProxyHandler(Proxy):
    def __init__(self, *args, **kwargs):
        self.proxy_list, self.black_list, self.ipv4_list = config.loadHost()
        super().__init__(*args, **kwargs)
    
    def handle_Host(self):
        Host_init = self.headers.get('Host', '')
        if not Host_init:
            Host_init = self.path
        host, _, port = Host_init.rpartition(':')
        try:
            port = int(port)
        except:
            host, port = Host_init, 443 if self.TLS else 80
        
        self.Host = (host, port)
        self.Host_in = (self.request.getpeername())
        
        self.Sock_args = tuple(self.sock_args.values())
        self.Sock_args_v6 = tuple(self.sock_args_v6.values())
        
        host_main = '.'.join(host_list[1:]) if len(host_list := host.split('.')) > 2 else host
        host_all = host
        
        if host_main in self.black_list:
            return self.do_BLOCK()
        elif host_main in self.proxy_list:
            return self.do_VPN()
        elif host_main in self.ipv4_list:
            return self.do_PROXY(False)
        else:
            return self.do_PROXY(True)


class ProxyServer():
    def __init__(self):
        self.Q = queue.Queue()
        self.Handler = ProxyHandler
        self.Host, self.Port = Host, Port

    def Proxy(self, Mode):
        with ThreadingHTTPServer((self.Host, self.Port), Mode) as httpd:
            self.Q.put(httpd)
            httpd.serve_forever()

    def start(self):
        thread = threading.Thread(target=self.Proxy, args=(self.Handler,))
        thread.start()
        thread.join()

    def stop(self):
        while not self.Q.empty():
            self.Q.get().shutdown()

       
if __name__ == '__main__':
    ProxyServer().start()
