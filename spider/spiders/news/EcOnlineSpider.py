import json
import time

import scrapy
from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider

"""
电商在线：行业资讯（全部的），阿里零距离

"""


class EcOnlineSpider(NewsSpider):
    name = "econline_news"

    allowed_domains = ["imaijia.com"]

    news_type_list = [
        {"shorthand": "tbsr", "name": "淘宝神人"},
        {"shorthand": "hlwgc", "name": "互联网观察"},
        {"shorthand": "wljr", "name": "物流金融"},
        {"shorthand": "aizn", "name": "AI智能"},
        {"shorthand": "wycx", "name": "出行文娱"},
        {"shorthand": "xls", "name": "新零售"},
        {"shorthand": "alljl", "name": "阿里零距离"}
    ]

    # 数据列表
    list_url = "http://www.imaijia.com/api/article/list"

    # 数据详情
    detail_url = "http://www.imaijia.com/api/article/getById"

    def __init__(self, *a, **kw):
        super(EcOnlineSpider, self).__init__(*a, **kw)

    def start_requests(self):
        pageNum = 1
        pageSize = 5
        for news_type in self.news_type_list:
            columnAlias = news_type.get("shorthand")
            yield scrapy.FormRequest(
                url=self.list_url,
                formdata={"pageNum": str(pageNum),
                          "pageSize": str(pageSize),
                          "columnAlias": columnAlias},
                meta=news_type,
                dont_filter=True,
                callback=self.parse
            )

    def parse(self, response):
        data_list = response.text
        data_list = json.loads(data_list)
        datas = data_list["data"]["datas"]
        if datas is not None and len(datas) != 0:
            for data in datas:
                yield scrapy.FormRequest(
                    url=self.detail_url,
                    formdata={"id": str(data['id']),
                              "previewFlag": "0"},
                    meta=response.meta,
                    callback=self.detail
                )
        else:
            return


    def detail(self, response):

        data_list = response.text
        data_list = json.loads(data_list)
        data = data_list["data"]

        publishTime = data['publishTime']
        timeArray = time.localtime(int(publishTime/1000))
        push_date = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        out_id = data['id']
        title = data['title']
        print(response.meta["name"])
        new_type = response.meta['name']
        source = '电商在线'
        digest = data["summary"]
        content = data["content"]
        source_url = response.url
        spider_source = 110

        # print(out_id, push_date, title, new_type, source, digest, source_url, spider_source)
        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )
