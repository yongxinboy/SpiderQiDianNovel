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
from bson.objectid import ObjectId

client = pymongo.MongoClient(host="127.0.0.1")
db = client.novel  # 库名dianping
collection = db.novelname

import redis  # 导入redis数据库

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

ii = 0


class qidianNovelSpider(scrapy.Spider):
    name = "qidianNovelWorksInfo"
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
            # if ii > 5:
            #     break
        print(start_urls)
        self.start_urls = start_urls

    def parse(self, response):
        classInfo = self.dict[response.url]
        objectid = classInfo['classid']
        objectid2 = ObjectId(objectid)
        pid = classInfo['pid']
        # num = classInfo['num']
        # if num > 3:
        #     return None
        html = response.body.decode('utf-8')
        selector = etree.HTML(html)
        workName = selector.xpath('//div[@class="book-info "]/h1/span/a[@class="writer"]/text()')
        novelName = selector.xpath('//div[@class="book-info "]/h1/em/text()')
        novelState = selector.xpath('//div[@class="book-info "]/p[@class="tag"]/span[@class="blue"]/text()')
        novelClass = selector.xpath('//div[@class="book-info "]/p[@class="tag"]/a[@class="red"]/text()')
        objClass=novelClass[0]
        sonClass=novelClass[1]
        print("小说名："+novelName[0])
        print("作者名："+workName[0])
        print("状态：" + novelState[0])
        print("小说分类："+objClass)
        print("小说分类2：" + sonClass)

        db.novelname.update({"_id": objectid2}, {"$set": {'workName': workName, 'novelName': novelName, 'novelState': novelState, 'objClass': objClass,'sonClass': sonClass}})


        print('--------end--------------')
# ---------------------------------------------------------------------------------------------------------------

# def updateMongo(self, workName,novelName,novelState,objClass,sonClass,objectid2):
    #     # classid = collection.update({'workName': workName,'novelName':novelName,'novelState':novelState,'objClass':objClass,'sonClass':sonClass,'pid': pid})
    #     classid = collection.update({"_id":objectid2 },{"$set":{'workName': workName, 'novelName': novelName, 'novelState': novelState, 'objClass': objClass, 'sonClass': sonClass}})
    #     return classid
