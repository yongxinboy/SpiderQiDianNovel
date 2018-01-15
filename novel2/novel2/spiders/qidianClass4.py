import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
# from urllib.request import urlopen
from scrapy.http import Request
from ..items import Novel2Item
#from novel2.items import Novel2Item
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
collection = db.novelclass2

import redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0)


class qidianClassSpider(scrapy.Spider):
    name = "qidianClass4"
    allowed_domains = ["qidian.com"]  # 允许访问的域
    start_urls = [
        "https://www.qidian.com/mm/all",
    ]

    # #每爬完一个网页会回调parse方法
    # def parse(self, response):
    #     print(response.body.decode('utf-8'))
    def parse(self, response):

        hxs = HtmlXPathSelector(response)
        hxsObj = hxs.select('//div[@class="work-filter type-filter"]/ul[@type="category"]/li[@class=""]/a')
        for secItem in hxsObj:
            item=Novel2Item()
            item['className'] = secItem.select('text()').extract()
            item['classUrl'] = secItem.select('@href').extract()
            item['classUrl'] = 'https:' + item['classUrl'][0]
            print(item['className'][0])
            print("======================")
            # print(classUrl)
            classid = self.insertMongo(item['className'][0],None)
            request = Request(item['classUrl'], callback=lambda response, pid=str(classid): self.parse_subClass(response, pid))
            #request = Request(classUrl, callback=lambda response, pid=ObjectId(str(classid)): self.parse_subClass(response, pid))
            yield request

    def parse_subClass(self, response,pid):

        hxs = HtmlXPathSelector(response)
        hxsObj = hxs.select('//div[@class="sub-type"]/dl[@class=""]/dd[@class=""]/a')
        for secItem in hxsObj:
            item = Novel2Item()
            item['className2'] = secItem.select('text()').extract()
            item['classUrl2'] = secItem.select('@href').extract()
            print(item['className2'])
            print('----------------------------')
            item['classUrl2'] = 'https:' +item['classUrl2'][0]
            print(item['classUrl2'])
            #classid = self.insertMongo(className2[0],ObjectId(pid))
            classid = self.insertMongo(item['className2'][0], ObjectId(pid))
            self.pushRedis(classid,pid, item['classUrl2'])

    def insertMongo(self, classname, pid):
        classid = collection.insert({'classname': classname, 'pid':pid})
        return classid

    def pushRedis(self, classid, pid, url):
        novelurl2 = '%s,%s,%s' % (classid,pid, url)
        r.lpush('novelurl2', novelurl2)

