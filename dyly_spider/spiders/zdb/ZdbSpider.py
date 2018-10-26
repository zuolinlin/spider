# -*- coding: utf-8 -*-
from scrapy import Request
from dyly_spider.items import ZdbItem
from dyly_spider.spiders.BaseSpider import BaseSpider


# 投资人物
class ZdbSpider(BaseSpider):

    # 自定义配置
    custom_settings = {
        'ITEM_PIPELINES': {
            'dyly_spider.pipelines.ZdbSpiderPipeline': 1,
        }
    }

    name = "zdb"
    allowed_domains = ["pedaily.cn"]
    # 抓取第1页数据
    start_urls = ['https://zdb.pedaily.cn/people/p{page}/'.format(page=page) for page in range(1, 2)]

    def __init__(self, *a, **kw):
        super(ZdbSpider, self).__init__(*a, **kw)

    def parse(self, response):
        self.log("*" * 100)
        self.log("列表地址===>" + response.url)
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
        item = ZdbItem()
        item['name'] = response.xpath("normalize-space(/html/body/div[3]/div[1]/div/"
                                      "div[2]/div[2]/h1/text())").extract_first()
        item['company'] = response.xpath("normalize-space(/html/body/div[3]/div[1]/div/div[2]/div[2]/div/span["
                                         "1]/text())").extract_first()
        return item
