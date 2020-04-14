import threading
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from lxml import etree
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
import re
import os


class ImgHandle(object):
    def __init__(self):
        self.header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
        self.url = 'http://www.706zz.com'
        self.img_dir_title = None
        self.create_widget()

    def create_widget(self):
        self.window = tk.Tk()
        self.window.title("爬取不羞涩图片")
        self.window.geometry("580x580")

        self.label1 = tk.Label(self.window, text='存放路径')
        self.label2 = tk.Label(self.window, text='选择分类')
        self.label3 = tk.Label(self.window, text='爬取页数')

        # 创建一个文本展示框，并设置尺寸
        self.info = tk.Text(self.window,width=70)

        # 下拉选择按钮:爬取类型
        self.num1 = tk.StringVar()
        self.cmb1 = ttk.Combobox(self.window, textvariable=self.num1)

        # 设置下拉菜单中的值
        self.cmb1['values'] = ('自拍偷拍', '亚洲色图', '欧美色图', '美腿丝袜', '清纯唯美', '乱伦熟女', '卡通动漫')
        self.cmb1.current(0)  # 设置默认值，即默认下拉框中的内容,默认值中的内容为索引，从0开始

        # 下拉选择按钮:爬取页数
        self.num2 = tk.StringVar()
        self.cmb2 = ttk.Combobox(self.window, textvariable=self.num2)

        # 设置下拉菜单中的值
        self.cmb2['values'] = (1, 2, 3, 4, 5)
        self.cmb2.current(0)  # 设置默认值，即默认下拉框中的内容,默认值中的内容为索引，从0开始

        # 输入框，显示选择的路径
        self.path = tk.StringVar()
        self.e = tk.Entry(self.window, show=None, width=8, textvariable=self.path)

        # button按钮
        self.t1_button = tk.Button(self.window, text='选择路径', relief=tk.RAISED, width=8, height=1, command=lambda:self.select_Path())

        # 清空输入框
        self.t2_button = tk.Button(self.window, text='清空路径', relief=tk.RAISED, width=8, height=1, command=lambda:self.clear_Path())

        # 提取按钮
        self.run_button = tk.Button(self.window,text="开始提取",relief=tk.RAISED,command=lambda:self.thread_it(self.run_run))

    def grid(self):
        '''组件布局'''
        self.label1.grid(row=1, column=1, padx=10, pady=10, ipadx=10, ipady=10)
        self.label2.grid(row=2, column=1, padx=10, pady=20, ipadx=10, ipady=10)
        self.cmb1.grid(row=2, column=2, padx=10, pady=20, ipadx=30, ipady=8)
        self.label3.grid(row=3, column=1, padx=10, pady=10, ipadx=10, ipady=10)
        self.cmb2.grid(row=3, column=2, padx=10, pady=20, ipadx=30, ipady=8)
        self.e.grid(row=1, column=2, padx=1, pady=10, ipadx=130, ipady=8)
        self.t1_button.grid(row=1, column=3, padx=10)
        self.t2_button.grid(row=1, column=4)
        self.run_button.grid(row=2, column=3)
        self.info.grid(row=4, rowspan=5, column=1, columnspan=4)

    def select_Path(self):
        """选取本地路径"""
        filepath = askdirectory()
        self.path.set(filepath)

    def clear_Path(self):
        """清空输入框中路径"""
        self.e.delete(0, "end")  # 从第一行清除到最后一行

    def get_pagenum(self):
        '''获取页数'''
        print(self.cmb2.get())
        return self.cmb2.get()

    def thread_it(self,func):
        '''将函数打包进线程'''
        t = threading.Thread(target=func)
        # 守护 !!!
        t.setDaemon(True)
        # 启动
        t.start()
        # 阻塞--卡死界面！
        # t.join()

    def get_newest_url(self):
        '''获取最新域名'''
        response = requests.get(url=self.url, headers=self.header)
        self.url = response.url
        print('最新域名：',self.url)
        self.info.insert('end','最新域名：%s\n'%self.url)

    def get_url(self):
        '''构造前几页页url列表'''
        base_url = self.url + "/tupian/list-"
        url_list = []
        for i in range(int(self.get_pagenum())):
            url = base_url + str(self.cmb1.get()) + "-" + str(self.get_pagenum() + ".html")
            print(url)
            url_list.append(url)
        return url_list

    def get_img_dir(self,url):
        '''获取图片目录url'''
        respont = requests.get(url=url,headers=self.header)
        responts = etree.HTML(respont.text)
        img_dir_list = responts.xpath('//*[@id="tpl-img-content"]/li')
        dir_list = []
        for dir in img_dir_list:
            img_dir_url = dir.xpath('./a/@href')
            img_dir_urls = self.url + img_dir_url[0]
            print(img_dir_urls)
            dir_list.append(img_dir_urls)
        return dir_list

    def get_img_url(self,url):
        '''获取目录下每一张图片url'''
        urls = self.get_img_dir(url)
        with ThreadPoolExecutor(10) as pool:
            pool.map(self.request_img_url, urls)

    def request_img_url(self, url):
        respont = requests.get(url=url, headers=self.header)
        html = respont.text.encode('latin1').decode('utf-8')
        responts = etree.HTML(html)
        img_url_list = responts.xpath('//div[@class["content"]]/img/@data-original')
        img_dir_title = responts.xpath('//a[@href="javascript:;"]/text()')
        self.img_dir_title = img_dir_title[1]
        print(img_url_list)
        with ThreadPoolExecutor(10) as pool:
            pool.map(self.download, img_url_list)

    def download(self, url):
        '''下载'''
        b = self.e.get()
        a = b + '\\' + self.img_dir_title + url.split('/')[-2] + url.split('/')[-1]
        print(a)
        img_name = self.img_dir_title + url.split('/')[-1]
        file_path = a + img_name
        print(file_path)
        try:
            if not os.path.exists(file_path):  # 如果不存在则下载写文件
                print("正在下载：{}".format(img_name))
                self.info.insert('end', "正在下载：{}\n".format(img_name))
                self.info.see('end')
                self.info.update()
                respont = requests.get(url=url, headers=self.header)
                with open(file_path, "wb") as f:
                    f.write(respont.content)
                    print('下载完成：{}\n'.format(img_name))
                    self.info.insert('end', "下载完成：{}\n".format(img_name))
                    self.info.see('end')
                    self.info.update()
        except Exception:
            print('下载{}出错'.format(img_name))

    def run_run(self):
        self.get_newest_url()
        for i in self.get_url():
            self.get_img_url(i)

if __name__ == '__main__':
    t = ImgHandle()
    t.grid()
    tk.mainloop()


