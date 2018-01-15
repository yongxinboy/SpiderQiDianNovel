import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup
from lxml import etree


from pymongo import MongoClient

client = MongoClient('localhost', 27017)

import redis

# r = redis.Redis(host='127.0.0.1', port=6379, db=0)
r = redis.Redis(host='127.0.0.1', port=6379, db=0, charset='utf-8')
urls = r.lrange('classnovelurl', 0, -1)

class qidianClassSpider2(scrapy.Spider):
    name = "qidianClass2"
    allowed_domains = ["qidian.com"]  # 允许访问的域
    start_urls = []
    for item in urls:
        classurl = bytes.decode(item)
        arr = classurl.split(',')  # 分割字符串
        start_urls.append(arr[1])
    # print(start_urls)
# =========================================
    #每爬完一个网页会回调parse方法
    # def parse(self, response):
    #     # print(response.body.decode('utf-8'))
    #     print(111111111111111111111111111111111)
# =================================================
    def parse(self, response):

        hxs = HtmlXPathSelector(response)
        hxsObj = hxs.select('//div[@class="sub-type"]/dl[@class=""]/dd[@class=""]/a')
        for secItem in hxsObj:
            className2 = secItem.select('text()').extract()
            classUrl2 = secItem.select('@href').extract()
            print(className2)
            print('----------------------------')
            classUrl2 = 'http:' + classUrl2[0]
            print(classUrl2)
            db = client.novelclass
            collection = db.noveltitle2  # 类别表
            classid = collection.insert({'classname2':className2, 'pid': None})
            id =db.noveltitle2.find()
            for item in id:
                print(item.get('_id'))
            classUrl = '%s,%s' % (item.get('_id'),classUrl2[0])  # 拼接字符串
            r.lpush("classnovelurl", classUrl)
