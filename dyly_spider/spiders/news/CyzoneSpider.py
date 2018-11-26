import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
创业邦
"""


class CyzoneSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "cyzone"
    allowed_domains = ["cyzone.cn"]
    # 最新
    start_urls = ["https://www.cyzone.cn/category/22/"
                  ]

    def __init__(self, *a, **kw):
        super(CyzoneSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        datas = response.xpath('//div[@class="list-inner"]')
        if datas is not None:
            for data in datas:
                detial_url = data.xpath('./div[@class="article-item clearfix"]/div[@class="item-pic pull-left"]/a/@href').extract_first()
                detial_url = "https:" +detial_url
                digest = data.xpath('./div[@class="article-item clearfix"]/div[@class="item-intro"]/p[@class="item-desc"]/text()').extract_first()
                yield Request(
                    detial_url,
                    meta={"digest": digest},
                    callback=self.detail
                )

    def detail(self, response):
        url = response.url
        digest = response.meta['digest']
        out_id = str(url)[30:-5]
        title = response.xpath('//div[@class="article-hd"]/h1/text()').extract_first()
        push_time = response.xpath('//div[@class="article-hd"]/div[@class="clearfix"]/div/span[3]/text()').extract_first()
        source = "创业邦"
        content = response.xpath('//div[@class="article-content"]//p//text()').getall()
        content = "".join(content).strip()
        new_type = "初创公司"
        spider_source = 27
        self.insert_new(
                out_id,
                push_time,
                title,
                new_type,
                source,
                digest,
                content,
                spider_source
                    )
