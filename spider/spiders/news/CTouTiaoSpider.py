# -*- coding: utf-8 -*-

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class CTouTiaoSpider(NewsSpider):
    """
    创头条
    """

    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 1
    # }

    name = "ctoutiao_news"

    news_type_list = [
        # {"code": "policy_china", "name": "政策"},
        {"code": "city/77", "name": "深圳市"},
        {"code": "cat/18", "name": "新三板"},
        {"code": "cat/50", "name": "区块链"},
        {"code": "cat/9", "name": "汽车交通"},
        {"code": "cat/19", "name": "行业"},
    ]
    domain = "http://www.ctoutiao.com"
    list_url = "http://www.ctoutiao.com/{news_type}/?p={page}"

    def __init__(self, *a, **kw):
        super(CTouTiaoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=1),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        # page = int(response.xpath("//p[@class='page-all']/a[@class='red']/text()").extract_first())
        # if page == 1:
        #     pages = int(RegExUtil.find_first("p=(\d+)", response.xpath("//p[@class='page-all']/a[last()]/@href")
        #                                      .extract_first()))
        #     for page in range(2, pages + 1):
        #         yield Request(
        #             self.list_url.format(news_type=response.meta.get("code"), page=page),
        #             meta=response.meta,
        #             dont_filter=True
        #         )

        items = response.xpath("//li/div[contains(@class, 'A_list Nclea')]")

        for item in items:
            response.meta.update({
                "title": item.xpath(".//h2/a/@title").extract_first(),
                "push_date": item.xpath(".//p/span[2]/text()").extract_first(),
            })

            # print(item.xpath(".//h2/a/@title").extract_first())
            # print(item.xpath(".//p/span[2]/text()").extract_first())
            # print(self.domain + item.xpath(".//h2/a/@href").extract_first())

            yield Request(
                self.domain + item.xpath(".//h2/a/@href").extract_first(),
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        # print(
        #     RegExUtil.find_first("/(\d+).html", response.url),
        #     response.meta.get("push_date"),
        #     response.meta.get("title"),
        #     response.meta.get("name"),
        #     "创头条",
        #     None,
        #     response.xpath("/html/body").extract_first(),
        #     response.url,
        #     42
        # )
        self.insert_new(
            RegExUtil.find_first("/(\d+).html", response.url),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("name"),
            "创头条",
            None,
            response.xpath("/html/body").extract_first(),
            response.url,
            42
        )

