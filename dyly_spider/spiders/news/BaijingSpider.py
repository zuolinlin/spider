

# -*- coding: utf-8 -*-
import json
import datetime

from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import XPathUtil, date_util
import time

class BaijingSpider(NewsSpider):
    """
    白鲸
    """
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 10,
        "CONCURRENT_REQUESTS": 1
    }

    name = "baijing_news"
    allowed_domains = ["baijingapp.com"]

    start_url = "http://www.baijingapp.com"

    def __init__(self, *a, **kw):
        super(BaijingSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_url,
            dont_filter=True
        )

    def parse(self, response):
        """
        机构列表
        :param response:
        :return:
        """
        print(response)
        data_list =response.xpath('//div[@class="aw-mod aw-article-list"]//div[@class="articleSingle"]')
        for data in data_list:
            detailurl =str(data.xpath('./div[@class="articleSingle-info"]/h1/a/@href').extract_first())
            title = data.xpath('./div[@class="articleSingle-info"]/h1/a/@title').extract_first()
            digest = data.xpath('./div[@class="articleSingle-info"]/div/p/text()').extract_first()
            strs = str(detailurl).split('/')
            out_id =strs[strs.__len__() -1]
            publishTime= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield Request(
                url=detailurl,
                meta={"out_id": out_id,
                      "title": title,
                      "publishTime": publishTime,
                      "digest": digest
                      },
                callback=self.detail
            )

    def detail(self,response):
        out_id =response.meta['out_id']
        title = response.meta['title']
        publishTime = response.meta['publishTime']
        digest = response.meta['digest']
        content =response.xpath("/html/body").extract_first()
        self.insert_new(
            out_id,
            publishTime,
            title,
            "资讯",
            "白鲸",
            digest,
            content,
            response.url,
            5
        )
        print("success")

    def get_data(self, req):
        body = json.loads(req.body)
        if body["code"] == 1:
            data = body["data"]
            if len(data.get("rows", [])) > 0:
                return data
            else:
                self.log_error("request failed：" + repr(body))
        else:
            self.log_error("request failed：" + repr(body))
