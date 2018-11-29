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


class IyiouSpider(NewsSpider):
    name = "iyiou_news"
    allowed_domains = ["iyiou.com"]
    # 最新
    start_urls = ["https://www.iyiou.com/index/getMoreNewpost/page/2/time/"]

    def __init__(self, *a, **kw):
        super(IyiouSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = json.loads(response.text)
        dts = data_list["data"]
        if dts is not None:
            for data in dts:
                title = data["title"]
                out_id = data["id"]
                push_data = data["time"]
                digest = data["introduction"]
                url = data["url"]
                source = data["source"]
                try:
                    new_type = data["industry"]["title"]
                except:
                    new_type = "综合"
                yield Request(
                    url=url,
                    meta={
                        "title": title,
                        "out_id": out_id,
                        "push_data": push_data,
                        "digest": digest,
                        "source": source,
                        "new_type": new_type

                    },
                    callback=self.detail

                )
        # 获取下一页的数据
        pages = 3387
        while self.current_page < pages:
            self.current_page += 1
            next_url = "https://www.iyiou.com/index/getMoreNewpost/page/" + str(self.current_page)+"/time/"
            yield Request(next_url, callback=self.parse)

    def detail(self, response):
        title = response.meta['title']
        out_id = response.meta['out_id']
        new_type = response.meta['new_type']
        digest = response.meta['digest']
        source = response.meta['source']
        newstime = response.meta['push_data']
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
            push_time = str(newstime)
        content = response.xpath('//div[@id="post_description"]').extract_first()
        spider_source = 29
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
