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
from bson.objectid import ObjectId
import pymongo

client = pymongo.MongoClient(host="127.0.0.1")
db = client.novel  # 库名dianping
collection = db.novelname

import redis  # 导入redis数据库

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

ii = 0


class qidianNovelSpider(scrapy.Spider):
    name = "qidianNovel"
    allowed_domains = ["qidian.com"]  # 允许访问的域

    def __init__(self):
        # global pid
        # 查询reids库novelurl
        # qidianNovelSpider.start_urls=["https://www.qidian.com/all",]
        start_urls = []
        urlList = r.lrange('novelurl', 0,9)
        print(urlList)
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
            ii += 1
            if ii > 9:
                break
        print(start_urls)
        self.start_urls = start_urls

    def parse(self, response):
        url = response.url
        classInfo = self.dict[url]
        objectid = classInfo['classid']
        pid = classInfo['pid']
        num = classInfo['num']
        if num > 3:
            return None
        try:
            hxs = HtmlXPathSelector(response)
            hxsObj = hxs.select('//div[@class="book-mid-info"]/h4/a')
            for secItem in hxsObj:
                className = secItem.select('text()').extract()
                classUrl = secItem.select('@href').extract()
                classUrl = 'https:' + classUrl[0]
                print(className[0])
                print(classUrl)
                classid =self.insertMongo(className[0],ObjectId(objectid))
                self.pushRedis(classid,objectid, classUrl)
        except Exception as err:
            print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
            print(err)
            print('---------------------------------')
            print(url)
            print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")

        nextPage = self.nextUrl(response)
            # sleep(0.3)
            # --------------------------不用调用方法直接取下一页------------------------------------------------------------------------------
        # nextPages= hxs.select('//li[@class="lbf-pagination-item"]/a[@class="lbf-pagination-next "]')
        # nextPages = nextPages.select('@href').extract()
        # nextPage = "https:" + nextPages[0]

        classInfo['num'] += 1
        self.dict[nextPage] = classInfo
        request = Request(nextPage, callback=self.parse,)
        try:
            yield request
        except Exception as err:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            print(err)
            print(url)
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        print('--------end--------------')
# ---------------------------------------------------------------------------------------------------------------
# ===================获取下一页链接方法=======================================================
    def nextUrl(self, response):
        hxs = HtmlXPathSelector(response)
        # nextPage = hxs.select('//li[@class="lbf-pagination-item"]/a[@class="lbf-pagination-next "]')
        nextPage = hxs.select('//a[@class="lbf-pagination-next "]')
        # print(nextPage.extract())
        if len(nextPage) == 1:
            nextPage = nextPage.select('@href').extract()
            nextPage = "https:" + nextPage[0]

            print('==============' + nextPage + '====================')
            return nextPage

            # =====================获取下一页链接结束==================================================


    def insertMongo(self, className, pid):
        classid = collection.insert({'classname': className, 'pid': pid})
        return classid


    def pushRedis(self, classid, pid, classUrl):
        novelnameurl = '%s,%s,%s,' % (classid, pid, classUrl)
        r.lpush('novelnameurl', novelnameurl)
