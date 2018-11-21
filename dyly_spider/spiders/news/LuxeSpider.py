import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class LuxeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "luxe"
    allowed_domains = ["luxe.co"]
    # 金融与科技
    start_urls = ["http://luxe.co/category/finance"
                  ]

    def __init__(self, *a, **kw):
        super(LuxeSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list =response.xpath('/html/body/div[2]/div/div/div[3]/div[@class="col-md-9 page-left"]//div')
        if data_list is not None:
           for data in data_list:
               title = data.xpath('./a/@title').get().strip()  # 标题
               data.xpath('')

    def detail(self, response):
        pass
