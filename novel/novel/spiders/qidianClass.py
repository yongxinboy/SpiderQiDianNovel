import scrapy
from scrapy.selector import HtmlXPathSelector
# from scrapy.http import Request
# from urllib.request import urlopen
from scrapy.http import Request
# from hello.items import ZhaopinItem
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
from lxml import etree


from pymongo import MongoClient

client = MongoClient('localhost', 27017)

import redis

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

class qidianClassSpider(scrapy.Spider):
    name = "qidianClass"
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
            classUrl='http:'+classUrl[0]
            # print(className)
            # print('----------------------------')
            # print(classUrl)
            db = client.novelclass
            collection = db.noveltitle  # 类别表
            classid = collection.insert({'classname':className, 'pid': None})
            id =db.noveltitle.find()
            for item in id:
                print(item.get('_id'))
            classUrl = '%s,%s' % (item.get('_id'),classUrl)  # 拼接字符串
            r.lpush("classnovelurl", classUrl)
