import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import datetime
from spider.spiders.news.NewsSpider import NewsSpider

"""
BTC123 ===快讯
"""


class BtcflashSpider(NewsSpider):
    """
        重新设置请求头的信息
    """
    name = "btcflash_news"
    allowed_domains = ["btc123.com"]

    # 设置，爬取1、2、3页的新闻
    start_urls = ["https://apioperate.btc123.com/api/content/selectPageFlashNews?pageNumber={n}&pageSize=30&sourceId=1".format(n=n) for n in range(1,5)]

    def __init__(self, *a, **kw):
        super(BtcflashSpider, self).__init__(*a, **kw)
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']['list']
            for item in items:
                out_id = item['id']
                title = item['title']
                new_type = "快讯"
                source = item['source']
                content = item['content']


                push_date = item['createTime']
                # newstime = item['createText']
                # ti = newstime[-2:]
                # if ti == "时前":
                #     houses = newstime[0:-3]
                #     dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                #         "%Y-%m-%d %H:%M")
                # elif ti == "天前":
                #     days = newstime[0:-2]
                #     dataTime = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
                # elif ti == "钟前":
                #     minute = newstime[0:-3]
                #     dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime(
                #         "%Y-%m-%d %H:%M")
                # elif ti == "周前":
                #     print(".....")
                # else:
                #     dataTime = newstime



                # print(out_id, push_date, title, new_type, source, content)

                self.insert_new(
                    out_id,
                    push_date,
                    title,
                    new_type,
                    source,
                    None,
                    content,
                    "",
                    53
                )
