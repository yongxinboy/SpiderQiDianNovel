# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from scrapy.selector import HtmlXPathSelector
# from scrapy.http import Request
# from urllib.request import urlopen
from scrapy.http import Request
# from hello.items import ZhaopinItem
# from scrapy.spiders import CrawlSpider, Rule
from time import sleep
# from scrapy.linkextractors import LinkExtractor
from lxml import etree
import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient(host="127.0.0.1")
db = client.novel  # 库名dianping
collection = db.novelChapterInfo

import redis  # 导入redis数据库

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

ii = 0


class qidianNovelSpider(scrapy.Spider):
    name = "qidianNovelChapterContent"
    allowed_domains = ["qidian.com"]  # 允许访问的域

    def __init__(self):
        # global pid
        # 查询reids库novelurl
        #qidianNovelSpider.start_urls=["https://read.qidian.com/chapter/kbE0tc0oVoNrZK4x-CuJuw2/92LFs_xdtPXwrjbX3WA1AA2",]
        start_urls = []
        urlList = r.lrange('novelChapterUrl', 0,-1)
        ii = 0
        self.dict = {}
        for item in urlList:
            itemStr = str(item, encoding="utf-8")
            arr = itemStr.split(',')
            classid = arr[0]
            pid = arr[1]
            url = arr[2]
            start_urls.append(url)
            self.dict[url] = {"classid": classid, "pid": pid, "num": 0}
            # ii += 1
            # if ii > 10:
            #     break
        # print(start_urls)
        self.start_urls = start_urls

    def parse(self, response):
        classInfo = self.dict[response.url]
        objectid = classInfo['classid']
        objectid2 = ObjectId(objectid)
        pid = classInfo['pid']
        num = classInfo['num']
        ii = ""
        #==================================================================================
        html = response.body.decode('utf-8')
        selector = etree.HTML(html)
        novelChaptersContents = selector.xpath('//div[@class ="read-content j_readContent"]/p')
        # print(novelChaptersContent)
        for item in novelChaptersContents:
            novelChaptersContent=item.text
            # print(novelChaptersContent)
            ii = novelChaptersContent + ii
            # classid = collection.insert({'content': ii, 'pid': pid})
            db.novelChapterInfo.update({"_id": objectid2}, {"$set": {'novelChaptersContent':ii}})
        # sleep(0.3)
        print('------------------------------------------------------')

# ---------------------------------------------------------------------------------------------------------------
    # def nextChapter(self, response):
    #     hxs = HtmlXPathSelector(response)
    #     nextChapter = hxs.select('//div[@"chapter-control dib-wrap"]/a[@id = "j_chapterNext"]')
    #     # print(nextPage.extract())
    #     if len(nextChapter) == 1:
    #         nextChapter = nextChapter.select('@href').extract()
    #         nextChapter= "https:" + nextChapter[0]
    #         print('==============' + nextChapter + '====================')
    #         return nextChapter

