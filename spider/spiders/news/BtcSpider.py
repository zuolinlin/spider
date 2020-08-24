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
from spider.spiders.news.NewsSpider import NewsSpider

"""
BTC123 ====区块链，人物专访
"""


class TmtSpider(NewsSpider):
    """
        重新设置请求头的信息
    """
    name = "btc123_news"
    allowed_domains = ["btc123.com"]

    # 区块链1、2、3页的新闻
    news_type_url_list_Blockchain = ['https://apioperate.btc123.com/api/content/findArticleByCategoryId?pageNumber={n}&categoryId=37'.format(n = n) for n in range(1,4)]
    # 人物专访1、2、3页的新闻
    new_type_url_list_Interview = ['https://apioperate.btc123.com/api/content/findArticleByCategoryId?pageNumber={n}&categoryId=35'.format(n = n) for n in range(1,4)]
    start_urls = news_type_url_list_Blockchain + new_type_url_list_Interview

    base_url = "https://www.btc123.com/news/"

    def __init__(self, *a, **kw):
        super(TmtSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            # print(url)
            yield Request(
                url,
                dont_filter = False
            )

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']['list']
            for item in items:
                out_id = item['id']
                push_date = item['createTime']
                title = item['title']
                source = item['source']
                digest = item['summary']

                categoryId = response.url[-2:]

                detail_url = self.base_url + str(out_id)

                yield Request(
                    detail_url,
                    meta={
                        "out_id": out_id,
                        'push_date': push_date,
                        "title": title,
                        "source": source,
                        "digest": digest,
                        "categoryId": categoryId
                    },
                    callback=self.detail
                )

    def detail(self, response):
        out_id = response.meta['out_id']
        push_date = response.meta['push_date']
        title = response.meta['title']
        source = response.meta['source']
        digest = response.meta['digest']
        categoryId = response.meta['categoryId']

        # print(categoryId)
        if str(categoryId) == "37":
            new_type = "区块链"
        elif str(categoryId) == "35":
            new_type = "人物专访"
        content = response.xpath('/html/body').extract_first()

        # print(out_id, push_date, title, source, digest, new_type)
        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            response.url,
            53
        )
