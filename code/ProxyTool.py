# -*- coding: utf-8 -*-

import os, json
import socket, select
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class ProxyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = directory
        self.path_data = os.path.join(os.path.dirname(self.directory), 'data')
        os.makedirs(os.path.dirname(self.path_data), exist_ok=True)
        try:
            with open(os.path.join(self.path_data, 'host.json'), 'rt') as fd:
                self.hosts = json.load(fd)
            with open(os.path.join(self.path_data, 'blocklist.txt'), 'rt') as fd:
                block_list = fd.readlines()
            self.block_list = [host[:-1] if '\n' in host else host for host in block_list]
            with open(os.path.join(self.path_data, 'proxylist.txt'), 'rt') as fd:
                proxy_list = fd.readlines()
            self.proxy_list = [host[:-1] if '\n' in host else host for host in proxy_list]
        except:
            self.hosts = {}
            self.block_list = []
            self.proxy_list = []
        
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
        
        host_main = '.'.join(host.split('.')[1:])
        
        if host in self.block_list or host_main in self.block_list:
            print('A:', host, port)
            return self.do_BLOCK()
        elif host in self.proxy_list or host_main in self.proxy_list:
            print('B:', host, port)
            return self.do_FORWARD()
        else:
            print('C:', host, port)
            return self.do_PROXY(host, port)
            
    def do_PROXY(self, host, port):
        host_ip = self.hosts.get(host, None)
        if host_ip:
            pass
        else:
            try:
                host_ip = socket.getaddrinfo(host, port, socket.AF_INET6)[0][-1][0]
            except:
                host_ip = socket.getaddrinfo(host, port, socket.AF_INET)[0][-1][0]
        if ':' in host_ip:
            remote_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.TLS:
            try:
                remote_socket.connect_ex((host_ip, port))
                self.wfile.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self.handle_tcp(self.connection, remote_socket)
            except:
                self.wfile.write(b'HTTP/1.1 501 Connection Error\r\n\r\n')
        else:
            del self.headers['Proxy-Connection']
            self.headers['Connection'] = 'close'
            
            path = self.path.rpartition(self.Host)[-1]
            send_data = ' '.join([self.command, path, self.request_version]).encode()
            send_data += b'\r\n'
            
            raw_headers = ["{key}: {value}\r\n".format(key=key, value=value) for key, value in self.headers.items()]
            headers = ''.join(raw_headers).encode() + b'\r\n'
            
            self.req_payload = b''

            if self.command in ('POST', 'PUT'):
                self.req_payload = self.read_payload()
            send_data = send_data + headers + self.req_payload
            
            try:
                remote_socket.connect_ex((host_ip, port))
                remote_socket.sendall(send_data)
                data = self.receive_data(remote_socket)
                self.wfile.write(data)
            except:
                self.wfile.write(b'HTTP/1.1 404 Connection Error\r\n\r\n')
                
    def do_FORWARD(self):
        client_socket = self.request
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect_ex(('localhost', 8087))
        raw_headers = ["{key}: {value}\r\n".format(key=key, value=value) for key, value in self.headers.items()]
        headers = ''.join(raw_headers).encode() + b'\r\n'
        server_socket.sendall(self.raw_requestline+headers)
        if self.TLS:
            self.handle_tcp(server_socket, client_socket)
        else:
            self.forward_data(server_socket, client_socket)
    
    def do_BLOCK(self):
        if self.TLS:
            self.wfile.write(b'HTTP/1.1 501 Connection Error\r\nError: 501\r\n\r\n')
        else:
            self.wfile.write(b'HTTP/1.1 501 Connection Error\r\nError: 501\r\n\r\n')
    
    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            while True:
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = sock.recv(1024)
                    if len(data) <= 0:
                        break
                    result = self.send_data(remote, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
                
                if remote in r:
                    data = remote.recv(4096)
                    if len(data) <= 0:
                        break
                    result = self.send_data(sock, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
        except Exception as error:
            pass
        finally:
            sock.close()
            remote.close()
    
    def send_data(self, sock, data):
        bytes_sent = 0
        while True:
            r = sock.send(data[bytes_sent:])
            if r < 0:
                return r
            bytes_sent += r
            if bytes_sent == len(data):
                return bytes_sent
    
    def receive_data(self, sock):
        data = b''
        while True:
            recv_data = sock.recv(4096)
            if not recv_data:
                break
            data += recv_data
        sock.close()
        return data
        
    def read_payload(self):
        payload = b''
        if 'Content-Length' in self.headers:
            try:
                payload_len = int(self.headers.get('Content-Length', 0))
                payload = self.rfile.read(payload_len)
            except:
                print('handle_method_urlfetch read payload failed')
        elif 'Transfer-Encoding' in self.headers:
            payload = ""
            while True:
                chunk_size_str = self.rfile.readline(65537)
                chunk_size_list = chunk_size_str.split(";")
                chunk_size = int("0x"+chunk_size_list[0], 0)
                if len(chunk_size_list) > 1 and chunk_size_list[1] != "\r\n":
                    print("chunk ext: %s", chunk_size_str)
                if chunk_size == 0:
                    while True:
                        line = self.rfile.readline(65537)
                        if line == "\r\n":
                            break
                        else:
                            print("entity header:%s", line)
                    break
                payload += self.rfile.read(chunk_size)
        # self.req_payload = payload
        return payload

    def forward_data(self, sock, remote):
        while True:
            recv_data = sock.recv(2048)
            if not recv_data:
                break
            remote.sendall(recv_data)
        sock.close()
        remote.close()
        


def main():
    try:
        with open(os.path.join(os.getcwd(), 'data', 'config.json'), 'rt') as fd:
            hostconfig = json.load(fd)
        Host = hostconfig['host']
        Port = int(hostconfig['port'])
        with ThreadingHTTPServer((Host, Port), ProxyHandler) as httpd:
            # print("Proxy serving at port", Port)
            httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.socket.close()
        
if __name__ == '__main__':
    main()
