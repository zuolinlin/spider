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
懒熊体育
"""


class TmtSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "tmt"
    allowed_domains = ["tmtpost.com"]
    # 最新
    start_urls = ["http://www.tmtpost.com/ajax/common/get?url=%2Fv1%2Finvestment%2Fshort_news&data=%26limit%3D6235%26offset%3D0"
                  ]

    def __init__(self, *a, **kw):
        super(TmtSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']
            for item in items:
                out_id = item['id']
                push_time = item['time_created']
                title = item['short_news_title']
                new_type = "融资快讯"
                source = "钛媒体"
                content_html= item['short_news_main']
                content_html_select =str_to_selector(content_html)
                content = content_html_select.xpath('//p/text()').getall()
                content = "".join(content).strip()
                spider_source = 19
                digest = None
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
