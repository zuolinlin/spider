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
投资界---人物和投资
"""


class PedailySpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "pedaily"
    allowed_domains = ["pedaily.cn"]
    # 最新
    base_url = "https://www.lieyunwang.com"
    news_type_url_list = [
        {"code": "https://pe.pedaily.cn/vcpe/", "name": "VC/PE"},
        {"code": "https://pe.pedaily.cn/angel-investment/", "name": "天使"},
        {"code": "https://pe.pedaily.cn/new-third-board/", "name": "新三板"},
        {"code": "https://people.pedaily.cn/interview/", "name": "对话投资人"},
        {"code": "https://people.pedaily.cn/investor100/", "name": "投资界100"},
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
            data_list = response.xpath('//div[@class="news-list"]/ul[@id="newslist-all"]')
            if data_list is not None:
                for data in data_list:
                    detial_url = data.xpath('./li/h3/a/@href').extract_first()
                    title = data.xpath('./li/h3/a/text()').extract_first()
                    url = response.url
                    new_type = str(url).split('/')[3]
                    yield Request(
                        detial_url,
                        meta={"title": title,
                              "new_type": new_type},
                        dont_filter=True,
                        callback=self.detail
                    )
            # 请求下一页
            time.sleep(3)
            # 获取下一页
            next_url = response.xpath('//div[@class="page-list page"]/a[last()]/@href').extract_first()
            if not next_url:
                return
            else:
                yield Request(next_url, callback=self.parse)

    def detail(self, response):
        title = response.meta["title"]
        new_type = response.meta["new_type"]
        detial_url = response.url
        out_id = str(detial_url).split("/")[4][0:-6]
        push_time = response.xpath('//div[@class="news-show"]/div[@class="info"]/div[@class="box-l"]/span[@class="date"]/text()').extract_first()
        try:
            digest = response.xpath('//div[@class="subject"]/text()').extract_first()
        except:
            digest = None
        content = response.xpath('//div[@class="news-content"]').extract_first()
        source = "投资界"
        spider_source = 35
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

