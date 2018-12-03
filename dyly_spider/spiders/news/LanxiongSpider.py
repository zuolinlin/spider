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


class LanxiongSpiderSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "lanxiong_new"
    allowed_domains = ["lanxiongsports.com"]
    # 最新
    start_urls = ["http://www.lanxiongsports.com/mservice/?c=news&a=index&format=json&cid=1&page=1&_=1542944227272"
                  ]

    def __init__(self, *a, **kw):
        super(LanxiongSpiderSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['items']
            pager =jsondata['pager']
            nextPage = pager['nextPage']
            for item in items:
                url = item['url']
                out_id = item['id']
                title = item['title']
                digest = item['summary']
                yield Request(
                      url,
                      meta={
                            "out_id": out_id,
                            "title": title,
                            "digest": digest},
                      callback=self.detail
                            )
            # 请求下一页
            if  nextPage == 0:
                return
            else:
                next_url ="http://www.lanxiongsports.com/mservice/?c=news&a=index&format=json&cid=1&page=" + str(nextPage)+"&_=1542944227272"
                yield Request(url =next_url,
                              callback=self.parse)

    def detail(self, response):
        out_id = response.meta['out_id']
        title = response.meta['title']
        digest = response.meta['digest']
        push_time = response.xpath('//*[@id="main"]/div[1]/div/div/span/text()').extract_first()
        new_type = "大公司"
        source = "懒熊体育"
        spider_source = 17
        content = response.xpath('//div[@class="article or"]/div').extract_first()
        content = "".join(content)
        if not content:
            pass
        else:

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
