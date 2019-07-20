# -*- coding: utf-8 -*-

import tkinter as tk
import os, threading

from config import Config
from handler import ProxyServer

config = Config()
host, port = config.getConfig()

class ProxyGUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('HTTP Proxy')
        self.root.geometry('360x300')
        self.root.resizable(0, 0)
        
        main_Frame = tk.Frame(self.root)
        main_Frame.grid(row=0, column=0, padx=39, pady=15)
        
        toplabel = tk.Label(main_Frame, text='Welcome to the HTTP Proxy Server', font=('Microsoft YaHei', 12, 'normal'), anchor='center', bg='#CCE5FF', fg='#004085')
        toplabel.grid(row=0, column=0, columnspan=3, pady=10, ipadx=5, ipady=2)
        
        self.fun_Frame = tk.Frame(self.root)
        self.fun_Frame.grid(row=1, column=0, pady=0)

        button_Frame = tk.Frame(self.fun_Frame)
        button_Frame.grid(row=0, column=0, padx=0, pady=10)

        self.function = tk.Button(button_Frame, text='Start', width=8, bg='#007BEE', fg='#FFF', command=self.proxy_start)
        self.function.grid(row=0, column=0, padx=25, pady=10)
        self.setup = tk.Button(button_Frame, text='Setup', width=8, bg='#28A745', fg='#FFF', command=self.proxy_setup)
        self.setup.grid(row=0, column=1, padx=25, pady=10)

        output_Frame = tk.Frame(self.fun_Frame)
        output_Frame.grid(row=1, column=0, padx=0, pady=15)

        self.output = tk.Text(output_Frame, width=28, height=5, bg='lightgrey', font=('Microsoft YaHei', 10, 'normal'), padx=5, pady=5)
        self.output.pack(expand=1, fill='both')
        self.output['state'] = 'disabled'
        self.output.bind("<Key>", lambda _: "break")
        

        self.opt_Frame = tk.Frame(self.root)
        self.opt_Frame.grid(row=1, column=0, padx=0, pady=0)

        proxy_Frame = tk.LabelFrame(self.opt_Frame, text='Proxy Setup')
        proxy_Frame.grid(row=0, column=0, pady=5)

        host_Frame = tk.LabelFrame(self.opt_Frame, text='Host Rules')
        host_Frame.grid(row=1, column=0, pady=5)

        proxyhost = tk.Label(proxy_Frame, width=5, text='Host:', underline=0, anchor='w', fg='#00B') 
        proxyhost.grid(row=0, column=0, padx=5, pady=5)
        proxyport = tk.Label(proxy_Frame, width=5, text='Port:', underline=0, anchor='w', fg='#00B')
        proxyport.grid(row=1, column=0, padx=5, pady=5)
        
        self.var_proxyhost = tk.StringVar()
        self.var_proxyhost.set(host)
        self.var_proxyport = tk.StringVar()
        self.var_proxyport.set(port)
        proxyhostEntry = tk.Entry(proxy_Frame, textvariable=self.var_proxyhost, width=12)
        proxyhostEntry.grid(row=0, column=1, padx=5, pady=3, ipadx=1)
        proxyportEntry = tk.Entry(proxy_Frame, textvariable=self.var_proxyport, width=12)
        proxyportEntry.grid(row=1, column=1, padx=5, pady=3, ipadx=1)

        savebutton = tk.Button(proxy_Frame, text='Save', width=7, bg='#007BEE', fg='#FFF', command=self.proxy_save)
        savebutton.grid(row=0, column=2, padx=10, pady=4)
        returnbutton = tk.Button(proxy_Frame, text='Return', width=7, bg='#DC3545', fg='#FFF', command=self.proxy_return)
        returnbutton.grid(row=1, column=2, padx=10, pady=4)


        typerule_Frame = tk.Frame(host_Frame)
        typerule_Frame.grid(row=0, column=0, rowspan=2, pady=3)
        
        hostrule_Frame = tk.Frame(host_Frame)
        hostrule_Frame.grid(row=0, column=1, padx=5, pady=3)
        
        funrule_Frame = tk.Frame(host_Frame)
        funrule_Frame.grid(row=1, column=1, pady=3)

        self.var_radio = tk.StringVar()
        self.var_radio.set(True)
        radioblock = tk.Radiobutton(typerule_Frame, text='Proxy', underline=0, width=6, variable=self.var_radio, anchor='w', value=True)
        radioblock.grid(row=0, column=0, pady=2, padx=5, sticky='w')
        radioproxy = tk.Radiobutton(typerule_Frame, text='Block', underline=0, width=6, variable=self.var_radio, anchor='w', value=False)
        radioproxy.grid(row=1, column=0, pady=2, padx=5, sticky='w')

        hostrule = tk.Label(hostrule_Frame, width=5, text='Host:', underline=0, anchor='w', fg='#00B')
        hostrule.grid(row=0, column=0, padx=5)
        self.var_hostrule = tk.StringVar()
        hostEntry = tk.Entry(hostrule_Frame, textvariable=self.var_hostrule, width=14)
        hostEntry.grid(row=0, column=1, padx=5, pady=0, ipadx=0)

        addhost = tk.Button(funrule_Frame, text='Add', width=7, bg='#28A745', fg='#FFF', command=self.host_add)
        addhost.grid(row=0, column=0, padx=10, pady=2)
        delhost = tk.Button(funrule_Frame, text='Delete', width=7, bg='#28A745', fg='#FFF', command=self.host_del)
        delhost.grid(row=0, column=1, padx=10, pady=2)

        self.proxy_return()
        self.root.mainloop()
        
        
    def proxy_start(self):
        self.function['text'] = 'Stop'
        self.function['bg'] = '#DC3545'
        self.function['command'] = self.proxy_stop
        self.setup['state'] = 'disabled'
        
        self.server = ProxyServer()
        thread = threading.Thread(target=self.server.start, args=())
        thread.setDaemon(True)
        thread.start()
        
        msg_info = 'Proxy Server is running!'
        self.show_msg(msg_info)

    def proxy_stop(self):
        self.function['text'] = 'Start'
        self.function['bg'] = '#007BEE'
        self.function['command'] = self.proxy_start
        self.setup['state'] = 'normal'
        
        thread = threading.Thread(target=self.server.stop, args=())
        thread.setDaemon(True)
        thread.start()
        
        msg_info = 'Proxy Server has stopped!'
        self.show_msg(msg_info)

    def proxy_setup(self):
        self.fun_Frame.grid_forget()
        self.opt_Frame.grid(row=1, column=0, pady=0)
        
    def proxy_save(self):
        Host = {
                'Host': self.var_proxyhost.get().strip(),
                'Port': int(self.var_proxyport.get().strip()),
            }
        config.saveConfig(**Host)

    def proxy_return(self):
        self.opt_Frame.grid_forget()
        self.fun_Frame.grid(row=1, column=0, pady=0)

    def host_add(self):
        mode = True if int(self.var_radio.get()) else False
        
        hostlist = dict()
        
        if mode:
            hostlist['Proxy'] = self.var_hostrule.get().strip()
        else:
            hostlist['Block'] = self.var_hostrule.get().strip()
        
        config.saveHost(hostlist, True)

    def host_del(self):
        mode = True if int(self.var_radio.get()) else False
        
        hostlist = dict()
        
        if mode:
            hostlist['Proxy'] = self.var_hostrule.get().strip()
        else:
            hostlist['Block'] = self.var_hostrule.get().strip()
        
        config.saveHost(hostlist, False)
        
    def show_msg(self, Msg_info):
        self.output['state'] = 'normal'
        self.output.delete(0.0, tk.END)
        self.output.insert(tk.END, Msg_info)
        self.output['state'] = 'disabled'


if __name__ == '__main__':
    ProxyGUI()
