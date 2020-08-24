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
import logging

"""
投资界---人物和投资
"""


class PedailySpider(NewsSpider):
    custom_settings = {
          "DOWNLOAD_DELAY": 2,
    }

    name = "pedaily_news"
    allowed_domains = ["pedaily.cn"]
    # 最新
    base_url = "https://www.lieyunwang.com"
    news_type_url_list = [
        {"code": "https://pe.pedaily.cn/vcpe/", "name": "VC/PE"},
        {"code": "https://pe.pedaily.cn/angel-investment/", "name": "天使"},
        {"code": "https://pe.pedaily.cn/new-third-board/", "name": "新三板"},
        {"code": "https://people.pedaily.cn/interview/", "name": "对话投资人"},
        {"code": "https://people.pedaily.cn/investor100/", "name": "投资界100"},

        {"code": "https://news.pedaily.cn/i-tmt/", "name": "TMT"},
        {"code": "https://news.pedaily.cn/i-culture-media/", "name": "文化传播娱乐"},
        {"code": "https://news.pedaily.cn/i-consume/", "name": "消费"},
        {"code": "https://research.pedaily.cn/1/", "name": "研究"},

    ]

    list_url = "https://{}.pedaily.cn/{}/{}"

    def __init__(self, *a, **kw):
        super(PedailySpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        for news_url in self.news_type_url_list:
            yield Request(
                news_url["code"],
                dont_filter=True
            )

    def parse(self, response):
            data_list = response.xpath('//div[@class="news-list"]/ul[@id="newslist-all"]/li')

            if data_list is not None:
                for data in data_list:
                    detial_url = data.xpath('./div/h3/a/@href').extract_first()
                    title = data.xpath('./div/h3/a/text()').extract_first()
                    digest = data.xpath('./div/div/text()').extract_first()
                    url = response.url

                    new_types = str(url).split('/')[2]
                    if new_types == "research.pedaily.cn":
                        new_type = "research"
                    else:
                        new_type = str(url).split('/')[3]
                    yield Request(
                        detial_url,
                        meta={"title": title,
                              "new_type": new_type,
                              "digest": digest},
                        dont_filter=True,
                        callback=self.detail
                    )


            # # 请求下一页
            # time.sleep(1)
            # # 获取下一页
            # next_url = response.xpath('//div[@class="page-list page"]/a[last()]/@href').extract_first()
            # if not next_url:
            #     return
            # else:
            #     yield Request(next_url, callback=self.parse)

    def detail(self, response):
        title = response.meta["title"]
        new_type = response.meta["new_type"]
        detial_url = response.url
        out_id = str(detial_url).split("/")[4][0:-6]

        push_time = response.xpath('//div[@class="news-show"]/div[@class="info"]/div[@class="box-l"]/span[@class="date"]/text()').extract_first()
        if push_time is None:
            push_time = response.xpath("//div[contains(@class, 'box-l')]/span[contains(@class, 'date')]/text()").extract_first()

        digest = response.meta["digest"]
        content = response.xpath('//html/body').extract_first()
        source = "投资界"
        spider_source = 35

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     # content,
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
        pass

