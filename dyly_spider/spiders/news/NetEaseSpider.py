# -*- coding: utf-8 -*-
import json
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
初创公司  观点  区块链
"""


class NetEaseSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "netEase_news"
    allowed_domains = ["163.com"]

    start_urls = ["http://money.163.com/special/00253368/institutions.html"]

    def __init__(self, *a, **kw):
        super(NetEaseSpider, self).__init__(*a, **kw)
        self.browser =None

    def parse(self, response):
        data_list = response.xpath('//div[@class="colLM"]//li')
        if data_list is not None:
            for data in data_list:
                detial_url = data.xpath('./span[@class="article"]/a/@href').extract_first()
                push_time = data.xpath('./span[@class="atime f12px"]/text()').extract_first()
                push_time = str(push_time)[1:-1]
                yield Request(
                    detial_url,
                    meta={
                        "push_time": push_time
                    },
                    callback=self.detail
                )

            # 获取下一页
            next_url = response.xpath('//div[@class="pageList lrBothMar4 martop15"]/a[last()]/@href').extract_first()
            yield Request(
                next_url,
                callback=self.parse
            )

    def detail(self, response):
        title = response.xpath('//div[@id="epContentLeft"]/h1/text()').extract_first()
        url = response.url
        strs = str(url).split("/")
        out_id = strs[len(strs)-1][0:-5]
        push_time = response.meta["push_time"]
        new_type="互联网金融"
        source = response.xpath('//div[@id="epContentLeft"]/div/a[@id="ne_article_source"]/text()').extract_first()
        content = response.xpath('//div[@class="post_text"]').extract_first()
        spider_source = 43
        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            None,
            content,
            response.url,
            spider_source
        )
