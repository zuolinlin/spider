import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from dyly_spider.spiders.news.NewsSpider import NewsSpider


""""
华丽志
"""


class LuxeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "luxe"
    allowed_domains = ["luxe.co"]
    # 金融与科技
    start_urls = ["http://luxe.co/category/tech"
                  ]

    # news_type_url_list = [
    #     {
    #         "code": "http://luxe.co/category/tech",
    #         "name": "科技"},
    #     {
    #         "code": "http://luxe.co/category/finance",
    #         "name": "金融"},
    #
    # ]
    #
    # def start_requests(self):
    #     for news_url in self.news_type_url_list:
    #         yield Request(
    #             news_url["code"],
    #             dont_filter=True
    #         )

    def __init__(self, *a, **kw):
        super(LuxeSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = response.xpath('//div[@class="col-md-9 page-left"]//div//div[@class="col-md-7 col-6 right"]')
        if data_list is not None:
            for data in data_list:
                title = data.xpath('./h2/a/@title').get().strip()  # 标题
                digest = data.xpath('./p/text()').get().strip()  # 摘要
                push_date = data.xpath('./div/text()').get().strip()  # 日期
                url = data.xpath('./h2/a/@href').get().strip()  # URL
                out_id = url[20:]
                yield Request(
                    url,
                    meta={"title": title,
                          "digest": digest,
                          "push_date": push_date,
                          "out_id": out_id},
                    callback=self.detail
                )
            # 获取下一页的数据
            pages = 10
            while self.current_page < pages:
                self.current_page += 1
                next_url ="http://luxe.co/category/tech/page/"+ str(self.current_page)

                yield Request(next_url, callback=self.parse)
        else:
            return

    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_date']
        title = response.meta['title']
        digest = response.meta['digest']
        content = response.xpath('//div[@class="post-body content"]').extract()
        content = "".join(content)
        new_type = "科技"
        source = "华丽志"
        spider_source = 9

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
