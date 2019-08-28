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
    list_urls = ["http://www.cs.com.cn/ssgs/gsxw/index_{page}.shtml".format(page=page) for page in range(1, 3)]
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
        data_list =response.xpath("/html/body/div[6]/div[1]/ul//li")
        for item in data_list:
            print(item)
            publishTime='20'+str(item.xpath('./span/text()').extract_first())
            title = item.xpath('./a/text()').extract_first()
            url =  'http://www.cs.com.cn/ssgs/gsxw/'+str(item.xpath('./a/@href').extract_first())[2:]
            out_id =str(url).split('/')[-1][0:-5]
            yield Request(
                url,
                meta={"out_id": out_id,
                      "title": title,
                      "publishTime": publishTime,
                      "digest": None
                      },
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        content = response.xpath("/html/body").extract_first()
        self.insert_new(
            response.meta['out_id'],
            response.meta['publishTime'],
            response.meta['title'],
            "公司新闻",
            "中证网",
            None,
            content,
            response.url,
            8
        )

