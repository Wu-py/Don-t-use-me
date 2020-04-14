from concurrent.futures.thread import ThreadPoolExecutor
import requests
from lxml import etree
import os


class ImgHandle(object):
    def __init__(self, url, dir, page=1):
        self.header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
        self.url = url
        self.dir = dir
        self.page = page
        self.img_dir_title = ''
        self.style = '自拍偷拍'

    def get_newest_url(self):
        '''获取最新域名'''
        response = requests.get(url=self.url, headers=self.header)
        self.url = response.url
        print('最新域名：',self.url)

    def get_url(self):
        # 构造前几页url列表
        base_url = self.url + "/tupian/list-"
        url_list = []
        for i in range(self.page):
            url = base_url + self.style + "-" + str(i+1) + ".html"
            print(url)
            url_list.append(url)
        return url_list

    def get_img_dir(self,url):
        '''获取某一页图片目录url'''
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
        '''获取每一张图片url'''
        urls = self.get_img_dir(url)
        with ThreadPoolExecutor(5) as pool:
            pool.map(self.request_img_url, urls)

    def request_img_url(self, url):
        respont = requests.get(url=url, headers=self.header)
        html = respont.text.encode('latin1').decode('utf-8')
        responts = etree.HTML(html)
        img_url_list = responts.xpath('//div[@class["content"]]/img/@data-original')
        print(img_url_list)
        img_dir_title = responts.xpath('//a[@href="javascript:;"]/text()')
        self.img_dir_title = img_dir_title[1]
        with ThreadPoolExecutor(10) as pool:
            pool.map(self.download, img_url_list)

    def download(self, url):
        '''下载'''
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        file_path = self.dir + '\\' + self.img_dir_title + url.split('/')[-2] + url.split('/')[-1]
        img_name = self.img_dir_title + url.split('/')[-1]
        print(file_path)
        try:
            if not os.path.exists(file_path):
                print("正在下载：{}".format(img_name))
                respont = requests.get(url=url, headers=self.header)
                with open(file_path, "wb") as f:
                    f.write(respont.content)
                    print('下载完成:{}'.format(img_name))
        except Exception:
            print('下载：{}出错'.format(img_name))

    def run(self):
        self.get_newest_url()
        for i in self.get_url():
            self.get_img_url(i)


if __name__ == '__main__':
    dir = 'F:\\706zz'
    url = 'https://706zz.com'
    page = 1
    t = ImgHandle(url, dir, page)
    t.run()



