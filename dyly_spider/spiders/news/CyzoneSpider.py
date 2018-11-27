import json
import jsonpath
import scrapy
import time
import datetime
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
    base_url = "https://www.cyzone.cn"

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
                push_time = data.xpath('./div[@class="article-item clearfix"]/div[@class="item-intro"]/span[@class="item-push-info"]/em/text()').extract_first()
                ti = push_time[-2:]
                if ti == "时前":
                    houses = push_time[0:-3]
                    push_time = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                        "%Y-%m-%d %H:%M")
                elif ti == "天前":
                    days = push_time[0:-2]
                    push_time = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime(
                        "%Y-%m-%d %H:%M")
                else:
                    push_time = push_time
                yield Request(
                    detial_url,
                    meta={"digest": digest,
                          "push_time": push_time},
                    callback=self.detail
                )
            # 获取下一页的链接
            next_url = response.xpath('//div[@class="page-box"]/a[last()-1]/@href').extract_first()
            # page_no= next_url[40:-5]
            # last_pageno = response.xpath('//div[@class="page-box"]/a[last()-2]')
            yield Request(CyzoneSpider.base_url+next_url, callback=self.parse)

    def detail(self, response):
        url = response.url
        digest = response.meta['digest']
        push_time = response.meta['push_time']
        out_id = str(url)[30:-5]
        title = response.xpath('//div[@class="article-hd"]/h1/text()').extract_first()

        source = "创业邦"
        content = response.xpath('//div[@class="article-content"]').extract_first()
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
                response.url,
                spider_source
                    )
