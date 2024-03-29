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
猎云网
"""


class LieyunwangSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "lieyunwang"
    allowed_domains = ["lieyunwang.com"]
    # 最新
    start_urls = ["https://www.lieyunwang.com/latest/p1.html"]
    base_url = "https://www.lieyunwang.com"

    def __init__(self, *a, **kw):
        super(LieyunwangSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
            data_list = response.xpath('//div[@class="article-container"]/div[@class="article-bar clearfix"]')
            # print(data_list)
            if data_list is not None:
                for data in data_list:
                    # print(data)
                    detial_url = data.xpath('.//div[@class="article-info pore"]//a/@href').extract_first()
                    # print(detial_url)
                    title = data.xpath('.//div[@class="article-info pore"]/h2/a/text()').extract_first()
                    if title is None:
                        title = data.xpath('.//div[@class="article-info pore"]/a/text()').extract_first()

                    detial_url = LieyunwangSpider.base_url + detial_url
                    yield Request(
                        detial_url,
                        meta={"title": title},
                        callback=self.detail
                    )


            # 请求下一页
            # 获取下一页
            # 取消注释可爬取全部新闻
            # next_page = response.xpath('//div[@class="pagination-wrapper"]/ul/li[@class="next"]/a/@href').extract_first()
            # if not next_page:
            #     return
            # else:
            #     next_url = LieyunwangSpider.base_url + next_page
            #     yield Request(next_url, callback=self.parse)

    def detail(self, response):
        title = response.meta['title']
        push_time = response.xpath('//h1[@class="lyw-article-title"]/span[@class="time"]/text()').extract_first()
        detial_url = response.url
        out_id = str(detial_url).split("/")[4]
        new_type = "咨询"
        source = "猎云网"
        digest = response.xpath('//div[@class="article-digest mb20"]/text()').get().strip()
        content = response.xpath('//div[@class="main-text"]').extract_first()
        spider_source = 33

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     content,
        #     response.url,
        #     spider_source
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
