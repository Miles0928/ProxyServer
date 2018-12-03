# -*- coding: utf-8 -*-

import os, json, queue, logging
import socket, select, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from config import Config

config = Config()

logfile = config.proxyLog
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
logging.basicConfig(filename=logfile, level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

class ProxyHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = directory
        self.hosts, self.block_list, self.proxy_list = config.loadHost()
        
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
            logging.info('[Block] {} {}'.format(host, port))
            return self.do_BLOCK()
        elif host in self.proxy_list or host_main in self.proxy_list:
            logging.info('[Forward] {} {}'.format(host, port))
            return self.do_FORWARD()
        else:
            logging.info('[Direct] {} {}'.format(host, port))
            return self.do_PROXY(host, port)
            
    def do_PROXY(self, host, port):
        host_ip = self.hosts.get(host, None)
        if host_ip:
            pass
        else:
            try:
                host_ip = socket.getaddrinfo(host, port, socket.AF_INET6)[0][-1][0]
            except:
                try:
                    host_ip = socket.getaddrinfo(host, port, socket.AF_INET)[0][-1][0]
                except:
                    logging.info('[D2F] {} {}'.format(host, port))
                    return self.do_FORWARD()

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
                logging.warning("handle_method_urlfetch read payload failed.")
        elif 'Transfer-Encoding' in self.headers:
            payload = ""
            while True:
                chunk_size_str = self.rfile.readline(65537)
                chunk_size_list = chunk_size_str.split(";")
                chunk_size = int("0x"+chunk_size_list[0], 0)
                if len(chunk_size_list) > 1 and chunk_size_list[1] != "\r\n":
                    logging.info("chunk ext: {}".format(chunk_size_str))
                if chunk_size == 0:
                    while True:
                        line = self.rfile.readline(65537)
                        if line == "\r\n":
                            break
                        else:
                            logging.info("entity header: {}".format(line))
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
        

class ForwardHandler(ProxyHandler):
    def handle_host(self):
        self.Host = self.headers.get('Host', '')
        host, _, port = self.Host.rpartition(':')
        try:
            port = int(port)
        except:
            host, port = self.Host, 443 if self.TLS else 80
        
        host_main = '.'.join(host.split('.')[1:])
        
        if host in self.block_list or host_main in self.block_list:
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
