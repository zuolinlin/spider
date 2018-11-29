# -*- coding: utf-8 -*-
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
import datetime
import re
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
金色财经=== 新闻， 政策 地图 ，人物， 应用， 投研， 技术 ，百科
"""


class JinseSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "jinse_news"
    allowed_domains = ["jinse.com"]
    # 最新
    start_urls = ["https://api.jinse.com/v6/information/list?catelogue_key=news&limit=23&information_id=0&flag=down&version=9.9.9"]
    news_type_url_list = [
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=news&limit=23&information_id=0&flag=down&version=9.9.9", "name": "新闻"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=zhengce&limit=23&information_id=0&flag=down&version=9.9.9", "name": "政策"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=personage&limit=23&information_id=0&flag=down&version=9.9.9", "name": "人物"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=fenxishishuo&limit=23&information_id=0&flag=down&version=9.9.9", "name": "行情"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=application&limit=23&information_id=0&flag=down&version=9.9.9", "name": "应用"},

        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=capitalmarket&limit=23&information_id=0&flag=down&version=9.9.9", "name": "投研"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=tech&limit=23&information_id=0&flag=down&version=9.9.9", "name": "技术"},
        {"code": "https://api.jinse.com/v6/information/list?catelogue_key=baike&limit=23&information_id=0&flag=down&version=9.9.9", "name": "百科"},
    ]

    def __init__(self, *a, **kw):
        super(JinseSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        for news_url in self.news_type_url_list:
            yield Request(
                news_url["code"],
                dont_filter=True
            )

    def parse(self, response):
        jsons_data = json.loads(response.text)
        data_list = jsons_data['list']
        bottom_id = jsons_data['bottom_id']
        url = response.url
        new_type = str(url).split('catelogue_key=')[1].split("&limit")[0]
        if data_list is not None:
            for data in data_list:
                out_id = data['extra']["child_id"]
                title = data['title']
                detial_url = data['extra']["topic_url"]
                digest = data['extra']["summary"]
                yield Request(
                    url=detial_url,
                    meta={
                        "out_id": out_id,
                        "title": title,
                        "new_type": new_type,
                        "digest": digest
                    },
                    callback=self.detail

                )

        if bottom_id is not None:
            next_url = str(url).split("information_id=")[0] + "information_id=" + str(
                bottom_id) + "&flag=down&version=9.9.9"
            yield Request(
                url=next_url,
                callback=self.parse
            )

    def detail(self, response):
        out_id = response.meta['out_id']
        title = response.meta['title']
        new_type = response.meta['new_type']
        digest = response.meta['digest']
        newstime = response.xpath('//div[@class="article-info"]/div[@class="time"]/text()').extract_first()

        ti = newstime[-2:]
        if ti == "时前":
            houses = newstime[0:-3]
            push_time = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime("%Y-%m-%d %H:%M")
        elif ti == "天前":
            days = newstime[0:-2]
            push_time = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
        elif ti == "钟前":
            minute = newstime[0:-3]
            push_time = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime("%Y-%m-%d %H:%M")
        elif ti == "周前":
            print(".....")
        else:
            push_time = str(newstime).replace(r'/', '-').replace(r'/', '-').replace(r'/', ' ')
        content = response.xpath('//div[@class="js-article-detail"]').extract_first()
        source = "金色财经"
        spider_source = 31
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
