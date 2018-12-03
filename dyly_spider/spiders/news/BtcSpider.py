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
BTC123 ====区块链，对话投资人
"""


class TmtSpider(NewsSpider):
    """
        重新设置请求头的信息
    """
    name = "btc123_news"
    allowed_domains = ["btc123.com"]
    # 最新
    news_type_url_list = [
        {"code": "https://apibtc.btc123.com/v1/index/getArticleByCategoryId?pageSize=10000000&categoryId=7", "name": "区块链"},
        {"code": "https://apibtc.btc123.com/v1/index/getArticleByCategoryId?categoryId=1&pageSize=10000000", "name": "对话合格投资人"},
    ]
    base_url = "https://www.btc123.com/news/newsDetails/"

    def __init__(self, *a, **kw):
        super(TmtSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        for news_url in self.news_type_url_list:
            yield Request(
                news_url["code"],
                dont_filter=True
            )

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']
            for item in items:
                out_id = item['id']
                source = item['source']
                digest = item['summary']
                title = item['title']
                categoryId = item['categoryId']
                detail_url ='https://www.btc123.com/news/newsDetails/' + str(out_id),
                detail_url = detail_url[0]
                yield Request(
                    detail_url,
                    meta={
                        "out_id": out_id,
                        "source": source,
                        "digest": digest,
                        "title": title,
                        "categoryId": categoryId
                    },
                    callback=self.detail
                )

    def detail(self, response):
        out_id = response.meta['out_id']
        source = response.meta['source']
        digest = response.meta['digest']
        title = response.meta['title']
        categoryId = response.meta['categoryId']
        if str(categoryId) == "7":
            new_type = "区块链"
        elif str(categoryId) == "1":
            new_type = "对话投资人"
        content = response.xpath('//*[@id="newsDetails-box"]/input[@id="bind-content"]/@value').extract_first()
        self.insert_new(
            out_id,
            None,
            title,
            new_type,
            source,
            digest,
            content,
            response.url,
            53
        )
