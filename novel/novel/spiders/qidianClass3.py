# 方法二：
# response.url 获取当前的url
# bcollection = getMongodb()
# for url in self.urls:
#     url = str(url, encoding="utf-8")
#     url = url.split(',')
#     if url[1]==response.url:
#         links = response.xpath('//div[@class="sub-type"]/dl[@class=""]/dd/a')
#         for link in links:
#             print("***************")
#             print(url[0])
#             print(link.select("text()").extract()[0])
#             print(link.select('@href').extract()[0])
#             print("***************")
#             id = bcollection.insert({'list_child_name': link.select("text()").extract()[0], 'pid': url[0]})
#             self.red.lpush('bnovel_all_list', str(id) + "," + "https:" + link.select('@href').extract()[0])
