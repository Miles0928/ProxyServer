# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import os, threading

from config import Config
from handler import ProxyServer


class ProxyGUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('HTTP Proxy')
        self.root.geometry('325x240')
        self.root.resizable(0, 0)
        if os.path.exists(r'.\proxy.ico'):
            self.root.iconbitmap(r'.\proxy.ico')
        
        menu = tk.Menu(self.root, tearoff=False)
        self.root.config(menu=menu)
        
        optionmenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label='Options', menu=optionmenu)
        optionmenu.add_command(label='Setup', command=self.proxy_option)
        
        helpmenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=helpmenu)
        helpmenu.add_command(label='About', command=self.proxy_help)
        
        
        mainFrame_top = ttk.Frame(self.root)
        mainFrame_top.grid(row=0, column=0, padx=34, pady=10)
        
        mainLabel = tk.Label(mainFrame_top, text='Welcome to the HTTP Proxy Server', font=('Times', 12, 'bold'), anchor='center', bg='#CCE5FF', fg='#004085')
        mainLabel.grid(row=0, column=0, columnspan=3, pady=10, ipadx=5)

        mainFrame_middle = ttk.Frame(self.root)
        mainFrame_middle.grid(row=1, column=0, pady=10)
        
        self.start = tk.Button(mainFrame_middle, text='Start', width=8, bg='#DC3545', fg='#FFF', command=self.proxy_start)
        self.start.grid(row=0, column=0, padx=25)
        self.stop = tk.Button(mainFrame_middle, text='Stop', width=8, bg='#28A745', fg='#FFF', command=self.proxy_stop)
        self.stop.grid(row=0, column=1, padx=25)
        self.stop['state'] = 'disabled'
        

        mainFrame_down = ttk.Frame(self.root)
        mainFrame_down.grid(row=2, column=0, pady=15)
        
        self.output = tk.Text(mainFrame_down, width=25, height=4, bg='lightblue', font=('Microsoft YaHei', 10, 'normal'), padx=5, pady=5)
        self.output.pack(expand=1, fill='both')
        self.output['state'] = 'disabled'
        self.output.bind("<Key>", lambda _: "break")
        
        self.root.mainloop()
    
    def proxy_start(self):
        methods = (True, True)
        self.server = ProxyServer(methods)
        thread = threading.Thread(target=self.server.start, args=())
        thread.setDaemon(True)
        thread.start()

        self.start['state'] = 'disabled'
        self.stop['state'] = 'normal'
        
        msg_info = 'Proxy Server is running!'
        self.show_msg(msg_info)

    def show_msg(self, Msg_info):
        self.output['state'] = 'normal'
        self.output.delete(0.0, tk.END)
        self.output.insert(tk.END, Msg_info)
        self.output['state'] = 'disabled'

    def proxy_stop(self):
        thread = threading.Thread(target=self.server.stop, args=())
        thread.setDaemon(True)
        thread.start()
        self.stop['state'] = 'disabled'
        self.start['state'] = 'normal'
        
        msg_info = 'Proxy Server has stopped!'
        self.show_msg(msg_info)
        
    def proxy_help(self):
        helpPage(self.root)
        
    def proxy_option(self):
        optionPage(self.root)


class optionPage():
    def __init__(self, master):
        self.root = tk.Toplevel(master)
        self.root.title('HTTP Proxy')
        self.root.geometry('240x180')
        self.root.resizable(0, 0)
        if os.path.exists(r'.\proxy.ico'):
            self.root.iconbitmap(r'.\proxy.ico')
            
        self.config = Config()
        self.host_config = self.config.getConfig()
            
        mainFrame_top = ttk.Frame(self.root)
        mainFrame_top.grid(row=0, column=0, padx=38, pady=15)
        
        host = tk.Label(mainFrame_top, width=6, text='Host:', fg='#00B') 
        host.grid(row=0, column=0, pady=5)
        port_proxy = tk.Label(mainFrame_top, width=6, text='Port:', fg='#00B')
        port_proxy.grid(row=1, column=0, pady=5)
        port_forward = tk.Label(mainFrame_top, width=6, text='Port:', fg='#00B')
        port_forward.grid(row=2, column=0, pady=5)
        label_proxy = tk.Label(mainFrame_top, width=8, text='(Proxy)', fg='#00B', anchor='w')
        label_proxy.grid(row=1, column=2, pady=5, sticky='w')
        label_forward = tk.Label(mainFrame_top, width=8, text='(Forward)', fg='#00B', anchor='w')
        label_forward.grid(row=2, column=2, pady=5, sticky='w')
        
        self.var_host = tk.StringVar()
        self.var_host.set(self.host_config[0])
        self.var_port_proxy = tk.StringVar()
        self.var_port_proxy.set(self.host_config[1])
        self.var_port_forward = tk.StringVar()
        self.var_port_forward.set(self.host_config[2])
        hostEntry = tk.Entry(mainFrame_top, textvariable=self.var_host, width=16)
        hostEntry.grid(row=0, column=1, columnspan=2, pady=5)
        portEntry_proxy = tk.Entry(mainFrame_top, textvariable=self.var_port_proxy, width=7)
        portEntry_proxy.grid(row=1, column=1, pady=5)
        portEntry_forward = tk.Entry(mainFrame_top, textvariable=self.var_port_forward, width=7)
        portEntry_forward.grid(row=2, column=1, pady=5)

        mainFrame_middle = ttk.Frame(self.root)
        mainFrame_middle.grid(row=1, column=0, pady=5)
        
        savehost = tk.Button(mainFrame_middle, text='Save', width=6, bg='#007BEE', fg='#FFF', font=('Microsoft YaHei', 8, 'normal'), command=self.save)
        savehost.grid(row=0, column=0, padx=10)
        resethost = tk.Button(mainFrame_middle, text='Switch', width=6, bg='#28A745', fg='#FFF', font=('Microsoft YaHei', 8, 'normal'), command=self.switch)
        resethost.grid(row=0, column=1, padx=10)
        resethost = tk.Button(mainFrame_middle, text='Reset', width=6, bg='#DC3545', fg='#FFF', font=('Microsoft YaHei', 8, 'normal'), command=self.reset)
        resethost.grid(row=0, column=2, padx=10)
        
        self.root.mainloop()

    def save(self):
        host = self.var_host.get().strip()
        port_proxy = self.var_port_proxy.get().strip()
        port_forward = self.var_port_forward.get().strip()
        self.config.saveConfig(host, port_proxy, port_forward)
        self.root.destroy()
        
    def switch(self):
        host = self.var_host.get().strip()
        port_forward = self.var_port_proxy.get().strip()
        port_proxy = self.var_port_forward.get().strip()
        self.config.saveConfig(host, port_proxy, port_forward)
        self.root.destroy()
        
    def reset(self):
        self.var_host.set('')
        self.var_port_proxy.set('8000')
        self.var_port_forward.set('8001')


class helpPage():
    def __init__(self, master):
        pass

if __name__ == '__main__':
    Proxy_Windows()
