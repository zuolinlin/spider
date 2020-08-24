import json
import jsonpath
import scrapy
import time
import datetime
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from spider.spiders.news.NewsSpider import NewsSpider

"""
创业邦
"""


class CyzoneSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "cyzone"
    allowed_domains = ["cyzone.cn"]

    # '最新' 栏目
    # channel_id=5   为'初创'
    start_urls = ["https://www.cyzone.cn/api/v2/content/channel/getArticle?page={n}&channel_id=&created_at=1584408648"
                      .format(n=n) for n in range(1, 3)]
    # base_url = "https://www.cyzone.cn"

    def __init__(self, *a, **kw):
        super(CyzoneSpider, self).__init__(*a, **kw)
        # self.current_page = 1
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']

            for item in items:
                out_id = item['content_id']
                title = item['title']
                new_type = '资讯'
                source = '创业邦'
                push_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item['published_at']))
                detial_url = 'https:' + item['url']
                digest = item['description']

                yield Request(
                    detial_url,
                    meta={"out_id":out_id,
                          "push_time": push_time,
                          "title": title,
                          "new_type": new_type,
                          "source": source,
                          "digest": digest,
                          },
                    callback=self.detail
                )

    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        title = response.meta['title']
        new_type = response.meta['new_type']
        source = response.meta['source']
        digest = response.meta['digest']
        content =response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 27



        # print(
        #             out_id,
        #             push_time,
        #             title,
        #             new_type,
        #             source,
        #             digest,
        #             # content,
        #             response.url,
        #             spider_source
        # )
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
