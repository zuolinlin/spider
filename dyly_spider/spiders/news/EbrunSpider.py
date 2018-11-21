# -*- coding: utf-8 -*-
import json
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
异邦新闻
"""
class TechnodeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "ebrun"
    allowed_domains = ["ebrun.com"]
    news_type_list = [
        {"code": 1, "name": "初创公司报道"},
        # {"code": 2, "name": "观点"},
        # {"code": 3, "name": "区块链"},
        # {"code": 4, "name": "NodeBang"},
        # {"code": 5, "name": "科技快讯"},
    ]

    start_urls = ["http://www.ebrun.com/top/"]

    def __init__(self, *a, **kw):
        super(TechnodeSpider, self).__init__(*a, **kw)
        self.browser =None

    def parse(self, response):
        pass
