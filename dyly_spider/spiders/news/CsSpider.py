# -*- coding: utf-8 -*-
import re

from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class CsSpider(NewsSpider):
    """
    中证网-公司新闻
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "cs_news"
    allowed_domains = ["cs.com.cn"]

    list_url = "http://www.cs.com.cn/ssgs/gsxw/index.shtml"
    list_urls = ["http://www.cs.com.cn/ssgs/gsxw/index_{page}.shtml".format(page=page) for page in range(1, 10)]
    detail_url = "http://www.cs.com.cn/ssgs/gsxw"

    def __init__(self, *a, **kw):
        super(CsSpider, self).__init__(*a, **kw)
        self.list_urls.insert(0, self.list_url)

    def start_requests(self):
        for list_url in self.list_urls:
            yield Request(
                list_url,
                dont_filter=True
            )

    def parse(self, response):
        for item in response.xpath("/html/body/div[6]/div[1]/ul/li"):
            yield Request(
                self.detail_url + item.xpath("a/@href").extract_first()[1:],
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        detail = response.xpath("/html/body/div[8]/div[1]")
        self.insert_new(
            re.findall("http://www.cs.com.cn/ssgs/gsxw/201811/(.*).html", response.url)[0],
            detail.xpath("normalize-space(div[2]/div[1]/p[2]/em[1]/text())").extract_first(),
            detail.xpath("normalize-space(div[2]/h1/text())").extract_first(),
            "公司新闻",
            detail.xpath("normalize-space(div[2]/div[1]/p[2]/em[2]/text())").extract_first()[3:],
            None,
            detail.xpath("div[2]/div[2]/*[not(@class='page') and not(@class='article-list')]"),
            response.url,
            8
        )

