# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import os, threading

from config import Config
from handler import ProxyServer

config = Config()
server = ProxyServer()
localhost, port, socks = config.getConfig()

class indexPage():
    def __init__(self):
        self.root = infoPage = tk.Tk()
        infoPage.title('网络代理工具')
        infoPage.geometry('300x320')
        infoPage.resizable(0, 0)

        Fts_mainLabel = ('Microsoft YaHei', 12, 'bold')
        Fts_Label = ('Microsoft YaHei', 9, 'bold')
        Fts_Text = ('Microsoft YaHei', 9, 'normal')
        Fts_Button = ('Microsoft YaHei', 9, 'normal')
        Fts_minButton = ('Microsoft YaHei', 8, 'normal')
        
        try:
            infoPage.iconbitmap(f'{os.getcwd()}\ProxyServer.ico')
        except:
            pass
        
        Top_Frame = ttk.Frame(infoPage)
        Top_Frame.grid(row=0, column=0, padx=90, pady=15)
        mainlabel = tk.Label(Top_Frame, text='网络代理工具', font=Fts_mainLabel, anchor='center', bg='#D4EDDA', fg='#155724')
        mainlabel.grid(row=0, column=0, pady=0, ipadx=9)
        
        Mid_Frame = ttk.LabelFrame(infoPage, text='代理设置')
        Mid_Frame.grid(row=1, column=0, pady=0)
        Mid_Frame_L = ttk.Frame(Mid_Frame)
        Mid_Frame_L.grid(row=0, column=0, padx=5)
        Mid_Frame_R = ttk.Frame(Mid_Frame)
        Mid_Frame_R.grid(row=0, column=1, padx=5)
        
        localhostLabel = tk.Label(Mid_Frame_L, text='主机:', width=8, bg='#F8D7DA', fg='#721C24', font=Fts_Label)
        localhostLabel.grid(row=0, column=0, padx=5, pady=5)
        portLabel = tk.Label(Mid_Frame_L, text='端口:', width=8, bg='#F8D7DA', fg='#721C24', font=Fts_Label)
        portLabel.grid(row=1, column=0, padx=5, pady=5)
        socksLabel = tk.Label(Mid_Frame_L, text='代理:', width=8, bg='#F8D7DA', fg='#721C24', font=Fts_Label)
        socksLabel.grid(row=2, column=0, padx=5, pady=5)
        self.var_localhost = tk.StringVar()
        self.var_localhost.set(localhost)
        self.var_port = tk.StringVar()
        self.var_port.set(port)
        self.var_socks = tk.StringVar()
        self.var_socks.set(socks)
        self.localhostEntry = tk.Entry(Mid_Frame_L, textvariable=self.var_localhost, width=8, fg='#721C24', show='*', font=Fts_Text)
        self.localhostEntry.grid(row=0, column=1, padx=5)
        self.portEntry = tk.Entry(Mid_Frame_L, textvariable=self.var_port, width=8, fg='#721C24', show='*', font=Fts_Text)
        self.portEntry.grid(row=1, column=1, padx=5)
        self.socksEntry = tk.Entry(Mid_Frame_L, textvariable=self.var_socks, width=8, fg='#721C24', show='*', font=Fts_Text)
        self.socksEntry.grid(row=2, column=1, padx=5)
        
        self.funButton = tk.Button(Mid_Frame_R, text='启动', width=8, bg='#007BFF', fg='#FFF', font=Fts_Button, command=lambda: self.proxy_start())
        self.funButton.grid(row=0, column=0, padx=5, pady=8)
        self.saveButton = tk.Button(Mid_Frame_R, text='显示', width=8, bg='#28A745', fg='#FFF', font=Fts_Button, command=lambda: self.proxy_display())
        self.saveButton.grid(row=1, column=0, padx=5, pady=8)
        
        # login page button: call usr_login or clear_info function
        Down_Frame = ttk.LabelFrame(infoPage, text='域名规则')
        Down_Frame.grid(row=2, column=0, pady=10)
        
        Down_Frame_T = ttk.Frame(Down_Frame)
        Down_Frame_T.grid(row=0, column=0)
        Down_Frame_M = ttk.Frame(Down_Frame)
        Down_Frame_M.grid(row=1, column=0)
        Down_Frame_D = ttk.Frame(Down_Frame)
        Down_Frame_D.grid(row=2, column=0)
        
        self.var_type = tk.StringVar()
        self.var_type.set('0')
        proxyRadio = tk.Radiobutton(Down_Frame_T, text='代理', width=5, fg='#007BFF', variable=self.var_type, anchor='w', value='0')
        proxyRadio.grid(row=0, column=0, pady=0, padx=5, sticky='w')
        blockRadio = tk.Radiobutton(Down_Frame_T, text='拦截', width=5, fg='#DC3545', variable=self.var_type, anchor='w', value='1')
        blockRadio.grid(row=0, column=1, pady=0, padx=5, sticky='w')
        directRadio = tk.Radiobutton(Down_Frame_T, text='IPv4', width=5, fg='#28A745', variable=self.var_type, anchor='w', value='2')
        directRadio.grid(row=0, column=2, pady=0, padx=5, sticky='w')
        
        hostLabel = tk.Label(Down_Frame_M, text='域名:', width=8, bg='#D1ECF1', fg='#0C5460', font=Fts_Label)
        hostLabel.grid(row=0, column=0, padx=8, pady=5)
        self.var_hostrule = tk.StringVar()
        hostEntry = tk.Entry(Down_Frame_M, width=20, textvariable=self.var_hostrule, fg='#0C5460')
        hostEntry.grid(row=0, column=1, padx=8, pady=5)

        self.addButton = tk.Button(Down_Frame_D, text='添加', width=6, bg='#DDD', fg='#DC3545', font=Fts_minButton, command=lambda: self.host_add())
        self.addButton.grid(row=0, column=0, padx=10, pady=5)
        self.viewButton = tk.Button(Down_Frame_D, text='查看', width=6, bg='#DDD', fg='#DC3545', font=Fts_minButton, command=lambda: self.host_view())
        self.viewButton.grid(row=0, column=1, padx=10, pady=5)
        self.delButton = tk.Button(Down_Frame_D, text='移除', width=6, bg='#DDD', fg='#DC3545', font=Fts_minButton, command=lambda: self.host_del())
        self.delButton.grid(row=0, column=2, padx=10, pady=5)

        infoPage.mainloop()    
    
    def proxy_start(self):
        self.funButton['text'] = '暂停'
        self.funButton['bg'] = '#DC3545'
        self.funButton['command'] = self.proxy_stop
        self.saveButton['state'] = 'disabled'
        self.addButton['state'] = 'disabled'
        self.delButton['state'] = 'disabled'
        self.proxy_hidden()

        thread = threading.Thread(target=server.start, args=())
        thread.setDaemon(True)
        thread.start()

    def proxy_stop(self):
        self.funButton['text'] = '启动'
        self.funButton['bg'] = '#007BFF'
        self.funButton['command'] = self.proxy_start
        
        self.saveButton['state'] = 'normal'
        self.addButton['state'] = 'normal'
        self.delButton['state'] = 'normal'
        
        thread = threading.Thread(target=server.stop, args=())
        thread.setDaemon(True)
        thread.start()
    
    def proxy_display(self):
        self.saveButton['text'] = '保存'
        self.saveButton['command'] = self.proxy_save
        self.localhostEntry['show'] = ''
        self.portEntry['show'] = ''
        self.socksEntry['show'] = ''
        
    def proxy_hidden(self):
        self.saveButton['text'] = '显示'
        self.saveButton['command'] = self.proxy_display
        self.localhostEntry['show'] = '*'
        self.portEntry['show'] = '*'
        self.socksEntry['show'] = '*'
    
    def proxy_save(self):
        self.proxy_hidden()

        localHost = {
                'Host': self.var_localhost.get().strip(),
                'Port': int(self.var_port.get().strip()),
                'Socks': int(self.var_socks.get().strip()),
            }
        config.saveConfig(**localHost)
        
    def host_add(self):
        hostindex = {'0': "Proxy", '1': "Block", '2': "IPv4"}
        mode = self.var_type.get()
        if hostrule := self.var_hostrule.get().strip():
            hostlist = {hostindex[mode]: hostrule}
        else:
            return None
        self.var_hostrule.set('')
        config.saveHost(hostlist, True)

    def host_del(self):
        hostindex = {'0': "Proxy", '1': "Block", '2': "IPv4"}
        mode = self.var_type.get()
        if hostrule := self.var_hostrule.get().strip():
            hostlist = {hostindex[mode]: hostrule}
        else:
            return None
        self.var_hostrule.set('')
        config.saveHost(hostlist, False)
        
    def host_view(self):
        viewHost(self.root)
            
class viewHost():
    def __init__(self, master):
        self.root = hostPage = tk.Toplevel(master)
        hostPage.title('网络代理工具')
        hostPage.geometry('300x250')
        hostPage.resizable(0, 0)
        hostPage.attributes("-topmost", 1)

        Fts_mainLabel = ('Microsoft YaHei', 12, 'bold')
        Fts_Label = ('Microsoft YaHei', 9, 'bold')
        Fts_Text = ('Microsoft YaHei', 9, 'normal')
        Fts_Button = ('Microsoft YaHei', 9, 'normal')
        Fts_minButton = ('Microsoft YaHei', 8, 'normal')
        
        try:
            hostPage.iconbitmap(f'{os.getcwd()}\ProxyServer.ico')
        except:
            pass
        
        Top_Frame = ttk.Frame(hostPage)
        Top_Frame.grid(row=0, column=0, padx=90, pady=15)
        mainlabel = tk.Label(Top_Frame, text='网络代理工具', font=Fts_mainLabel, anchor='center', bg='#D4EDDA', fg='#155724')
        mainlabel.grid(row=0, column=0, pady=0, ipadx=9)
        
        Mid_Frame = ttk.LabelFrame(hostPage, text='域名规则')
        Mid_Frame.grid(row=1, column=0, pady=0)
        
        Mid_Frame_T = ttk.Frame(Mid_Frame)
        Mid_Frame_T.grid(row=0, column=0, pady=0)
        Mid_Frame_D = ttk.Frame(Mid_Frame)
        Mid_Frame_D.grid(row=1, column=0, padx=5, pady=0)
        
        Mid_Frame_BG = ttk.Frame(Mid_Frame_D)
        Mid_Frame_BG.grid(row=0, column=0, columnspan=2, rowspan=5, sticky='wens')
        
        self.var_type = tk.StringVar()
        self.var_type.set('0')
        proxyRadio = tk.Radiobutton(Mid_Frame_T, text='代理', width=5, fg='#007BFF', variable=self.var_type, command=lambda: self.host_select(), anchor='w', value='0')
        proxyRadio.grid(row=0, column=0, padx=5, sticky='w')
        blockRadio = tk.Radiobutton(Mid_Frame_T, text='拦截', width=5, fg='#DC3545', variable=self.var_type, command=lambda: self.host_select(), anchor='w', value='1')
        blockRadio.grid(row=0, column=1, padx=5, sticky='w')
        directRadio = tk.Radiobutton(Mid_Frame_T, text='IPv4', width=5, fg='#28A745', variable=self.var_type, command=lambda: self.host_select(), anchor='w', value='2')
        directRadio.grid(row=0, column=2, padx=5, sticky='w')
        proxyRadio.select()
        
        self.hostRule = [0]*6
        self.var_hostRule = [0]*6
        
        for i in range(6):
            self.var_hostRule[i] = tk.StringVar(hostPage)
            self.var_hostRule[i].set('')
            
            self.hostRule[i] = tk.Entry(Mid_Frame_D, textvariable=self.var_hostRule[i], width=15, font=Fts_Text)
            self.hostRule[i].grid(row=i//2, column=i%2, padx=5, pady=5)
            self.hostRule[i]['state'] = 'readonly'
        
        Down_Frame = ttk.Frame(hostPage)
        Down_Frame.grid(row=2, column=0, pady=10)
        
        previousbutton = tk.Button(Down_Frame, text='上一页', width=6, bg='#DDD', fg='#007BFF', command=lambda: self.previous(), font=Fts_minButton)
        previousbutton.grid(row=0, column=1, padx=25)
        nextbutton = tk.Button(Down_Frame, text='下一页', width=6, bg='#DDD', fg='#007BFF', command=lambda: self.next(), font=Fts_minButton)
        nextbutton.grid(row=0, column=2, padx=25)
        
        self.assign_init()
        
    def assign_init(self, mode='0'):
        hostindex = {'0': "Proxy", '1': "Block", '2': "IPv4"}
        colorindex = {'0': "#007BFF", '1': "#DC3545", '2': "#28A745"}
        proxy_list, block_list, ipv4_list = config.loadHost()
        hostlist = {'Proxy': proxy_list, 'Block': block_list, 'IPv4': ipv4_list}
        
        self.host_list = hostlist.get(hostindex[mode])
        self.host_color = colorindex.get(mode)
        
        course_sum = len(self.host_list)
        
        self.Page = (course_sum - 1)//6
        if self.Page < 0:
            self.Page = 0
        
        self.Re = course_sum%6
        self.page = 0
        
        if course_sum < 6:
            self.assignvalue(self.Re)
        else:
            self.assignvalue()
        
        
    def assignvalue(self, m=6):
        for i in range(m):
            j = 6*self.page + i
            self.hostRule[i]['fg'] = self.host_color
            self.var_hostRule[i].set(self.host_list[j])
            
        if m < 6:
            for i in range(m, 6):
                self.var_hostRule[i].set('')
    
    def previous(self):
        if self.page != 0:
            self.page -= 1
            self.assignvalue()
        else:
            pass

    def next(self):
        if self.page != self.Page:
            self.page += 1
            if self.page < self.Page:
                self.assignvalue()
            else:
                if self.Re != 0:
                    self.assignvalue(self.Re)
                else:
                    self.assignvalue()
        else:
            pass
    
    def host_select(self):
        mode = self.var_type.get()
        self.assign_init(mode)         
         
if __name__ == '__main__':
    indexPage()