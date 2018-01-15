# -*- coding: utf-8 -*-
import scrapy
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

client = pymongo.MongoClient(host="127.0.0.1")
db = client.novel  # 库名dianping
collection = db.novelChapterInfo

import redis  # 导入redis数据库

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

ii = 0


class qidianNovelSpider(scrapy.Spider):
    name = "qidianNovelChapterInfo"
    allowed_domains = ["qidian.com"]  # 允许访问的域

    def __init__(self):
        # global pid
        # 查询reids库novelurl
        # qidianNovelSpider.start_urls=["https://www.qidian.com/all",]
        start_urls = []
        urlList = r.lrange('novelnameurl', 0, -1)
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
            # if ii > 1:
            #     break
        print(start_urls)
        self.start_urls = start_urls

    def parse(self, response):
        classInfo = self.dict[response.url]
        objectid = classInfo['classid']
        pid = classInfo['pid']
        # num = classInfo['num']
        # if num > 3:
        #     return None
        html = response.body.decode('utf-8')
        selector = etree.HTML(html)
        novelChapters = selector.xpath('//ul[@class="cf"]/li/a')
        for item in novelChapters:
            novelChapter= item.text
            print(item.text)
            novelChapterUrl='https:'+item.get('href')
            print(novelChapterUrl)
            # print(item.get('href'))

            classid = self.insertMongo(novelChapter, objectid)
            self.pushRedis(classid, objectid, novelChapterUrl)

    def insertMongo(self,novelChapter, pid):
        classid = collection.insert({'novelChapter': novelChapter,'pid': pid})
        return classid

    def pushRedis(self, classid,pid, novelChapterUrl):
        novelChapterUrl = '%s,%s,%s' % ( classid , pid, novelChapterUrl)
        r.lpush('novelChapterUrl', novelChapterUrl)
