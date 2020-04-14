import os
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from lxml import etree


class Videos(object):
    def __init__(self, url, page, dire):
        self.url = url
        self.page = page
        self.dire = dire
        self.header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }

    def get_newest_url(self):
        '''获取最新域名'''
        response = requests.get(url=self.url, headers=self.header)
        self.url = response.url
        print('最新域名：',self.url)

    def handle_page_url(self):
        # https: // www.hhw989.com / shipin / list - 短视频 - 2.html
        urls = []
        for i in range(self.page):
            url = self.url + '/shipin/list-短视频-' + str(i+1) + '.html'
            urls.append(url)
        return urls

    def handle_video_url(self, index):
        # https: // www.hhw989.com / shipin / play - 89739.html?road = 1
        index_nub = index.split('/')[-1]
        url = self.url + '/shipin/play-' + str(index_nub) + '?road=1'
        return url


    def get_videos_urls(self):
        urls = self.handle_page_url()
        print(urls)
        video_urls = []
        for i in urls:
            response = requests.get(url=i, headers=self.header)
            responses = response.text.encode('latin1').decode('utf-8')
            html = etree.HTML(responses)
            # videos_name = html.xpath('//*[@id="grid"]/li/a/@title')
            videos_index = html.xpath('//*[@id="grid"]/li/a/@href')
            for index in videos_index:
                url = self.handle_video_url(index)
                print(url)
                video_urls.append(url)
        return video_urls

    def mp4(self):
        urls = self.get_videos_urls()
        print(urls)
        with ThreadPoolExecutor(50) as pool:
            pool.map(self.thread_request,urls)

    def thread_request(self, url):
        index = url.split('/')[-1].split('.')[0]
        response = requests.get(url=url, headers=self.header)
        responses = response.text.encode('latin1').decode('utf-8')
        html = etree.HTML(responses)
        mp4_url = html.xpath('//tr[@class="app_hide"]/td/input/@data-clipboard-text')[0]
        mp4_name = html.xpath('//*[@id="main-container"]/div[1]/div/span/a[4]/text()')[0]
        name = mp4_name + index
        print(mp4_name)
        self.download(mp4_url, name)

    def download(self, url, name):
        dire = self.dire
        if not os.path.exists(dire):
            os.mkdir(dire)
        video_name = dire +'\\' + name +'.mp4'
        if not os.path.exists(video_name):
            print('正在下载:', video_name)
            response = requests.get(url=url, headers=self.header)
            with open(video_name, 'wb') as f:
                f.write(response.content)
                print('下载完成', video_name)


if __name__ == '__main__':
    url = 'https://www.706zz.com'
    page = 5
    dire = 'F:\\706'
    v = Videos(url=url, page=page, dire=dire)
    v.get_newest_url()
    v.mp4()






