# -*- coding: utf-8 -*-
import json

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
from util import date_util


class ChinaVentureSpider(NewsSpider):
    """
    投资中国
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "chinaventure_news"
    allowed_domains = ["chinaventure.com.cn"]

    news_type_list = [
        {
            'code':83, 'name':'5G'
        }
    ]

    start_url = "https://rsdata.cvmedia.com.cn/api/getNewsListByChannel"

    def __init__(self, *a, **kw):
        super(ChinaVentureSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def start_requests(self):
        for news_type in self.news_type_list:
            formdata = {
                'channel_id': news_type.get('code'),
                'begin_num': 21,
                'size': 60,
                'page':1
            }

            print(formdata)
            news_type.update({'page': 1})
            yield Request(
                self.start_url,
                method='POST',
                body =json.dumps(formdata)
            )

    def parse(self, response):
        data = response.text
        print(data)

