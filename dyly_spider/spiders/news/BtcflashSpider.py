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
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
BTC123 ===快讯
"""


class BtcflashSpider(NewsSpider):
    """
        重新设置请求头的信息
    """
    name = "btcflash_news"
    allowed_domains = ["btc123.com"]
    start_urls = ["https://apibtc.btc123.com/v1/index/getFlashPage?pageSize=10000&pageNumber=1"
                  ]

    def __init__(self, *a, **kw):
        super(BtcflashSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']
            for item in items:
                out_id = item['id']
                source = item['source']
                content = item['content']
                title = item['title']
                newstime = item['createText']
                ti = newstime[-2:]
                if ti == "时前":
                    houses = newstime[0:-3]
                    dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                        "%Y-%m-%d %H:%M")
                elif ti == "天前":
                    days = newstime[0:-2]
                    dataTime = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
                elif ti == "钟前":
                    minute = newstime[0:-3]
                    dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime(
                        "%Y-%m-%d %H:%M")
                elif ti == "周前":
                    print(".....")
                else:
                    dataTime = newstime
                new_type = "快讯"
                self.insert_new(
                    out_id,
                    dataTime,
                    title,
                    new_type,
                    source,
                    None,
                    content,
                    "",
                    53
                )
