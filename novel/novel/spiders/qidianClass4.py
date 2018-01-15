import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
# from urllib.request import urlopen
from scrapy.http import Request
# from hello.items import ZhaopinItem
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor
from urllib.request import urlopen
#from urllib.request import Request
from bs4 import BeautifulSoup
from lxml import etree
from bson.objectid import ObjectId
import pymongo
client = pymongo.MongoClient(host="127.0.0.1")
db = client.novel            #库名dianping
collection = db.novelclass

import redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0)


class qidianClassSpider(scrapy.Spider):
    name = "qidianClass4"
    allowed_domains = ["qidian.com"]  # 允许访问的域
    start_urls = [
        "https://www.qidian.com/all",
    ]

    # #每爬完一个网页会回调parse方法
    # def parse(self, response):
    #     print(response.body.decode('utf-8'))
    def parse(self, response):

        hxs = HtmlXPathSelector(response)
        hxsObj = hxs.select('//div[@class="work-filter type-filter"]/ul[@type="category"]/li[@class=""]/a')
        for secItem in hxsObj:
            className = secItem.select('text()').extract()
            classUrl = secItem.select('@href').extract()
            classUrl = 'https:' + classUrl[0]
            print(className[0])
            print(classUrl)
            classid = self.insertMongo(className[0],None)
            request = Request(classUrl, callback=lambda response, pid=str(classid): self.parse_subClass(response, pid))
            yield request
            print("======================")
    def parse_subClass(self, response,pid):

        hxs = HtmlXPathSelector(response)
        hxsObj = hxs.select('//div[@class="sub-type"]/dl[@class=""]/dd[@class=""]/a')
        for secItem in hxsObj:
            className2 = secItem.select('text()').extract()
            classUrl2 = secItem.select('@href').extract()
            print(className2)
            print('----------------------------')
            classUrl2 = 'https:' + classUrl2[0]
            print(classUrl2)
            classid = self.insertMongo(className2[0], ObjectId(pid))
            self.pushRedis(classid, pid, classUrl2)

    def insertMongo(self, classname, pid):
        classid = collection.insert({'classname': classname, 'pid': pid})
        return classid

    def pushRedis(self, classid, pid, url):
        novelurl = '%s,%s,%s' % (classid, pid, url)
        r.lpush('novelurl', novelurl)

