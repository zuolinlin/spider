# -*- coding: utf-8 -*-
import json
from scrapy import Request
from dyly_spider.spiders.BaseSpider import BaseSpider
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class TechnodeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "technode_news"
    allowed_domains = ["cn.technode.com"]

    start_urls = ["https://cn.technode.com/post/category/startups/"       # 初创公司报道
                 # "https://cn.technode.com/post/category/technode-talks/",  # 观点
                 # "https://cn.technode.com/post/category/blockchain/",      # 区块链
                 #  "https://cn.technode.com/nodebang/",                      # nodebang
                 #  "https://cn.technode.com/newsnow/"                       # 科技快讯
                  ]

    def __init__(self, *a, **kw):
        super(TechnodeSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//*[@id="inner-wrap"]/div[5]/div/div/div/div/div/div[1]/div[@class="td_mod_wrap td_mod9 "]')
        #
        for data in data_list:
            #  标题
            title = data.xpath('.//div[@class="item-details"]/h3/a/text()').get().strip()
            #  新闻来源
            source = data.xpath('.//div[@class="item-details"]/h3/a/@href').get().strip()
            #  时间
            pushTime = data.xpath('.//div[@class="item-details"]/div[@class="meta-info"]/time/text()').get().strip()
            # 摘要


        print(data_list)
        pass
