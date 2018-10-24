# -*- coding: utf-8 -*-
from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider


# 投资人物
class ZdbSpider(BaseSpider):

    name = "zdb"
    allowed_domains = ["pedaily.cn"]
    domain = 'https://zdb.pedaily.cn';
    start_urls = ['https://zdb.pedaily.cn/people/p{page}/'.format(page=page) for page in range(1, 11)]

    def __init__(self, *a, **kw):
        super(ZdbSpider, self).__init__(*a, **kw)

    def parse(self, response):
        self.log("*" * 100)
        self.log("列表地址：" + response.url)
        self.log("*" * 100)
        items = response.xpath('//*[@id="people-list"]/li')
        for item in items:
            yield Request(
                item.xpath('div[1]/a/@href').extract_first(),
                dont_filter=True,
                headers={},
                callback=self.detail
                )

    def detail(self, response):
        self.log("*" * 100)
        self.log("投资人物姓名：" + response.xpath("normalize-space(/html/body/div[3]/div[1]/div/"
                                            "div[2]/div[2]/h1/text())").extract_first())
        self.log("所属公司：" + response.xpath("normalize-space(/html/body/div[3]/div[1]/div/div[2]/div[2]/div/span["
                                          "1]/text())").extract_first())
        self.log("*" * 100)

