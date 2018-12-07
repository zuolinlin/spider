from dyly_spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json
from util.XPathUtil import str_to_selector

"""
速途网 == 电商、o2o、游戏、it、物联网、智能硬件、移动互联网
"""


class SootooSpider(NewsSpider):
    name = "sootoo_news"
    allowed_domains = ["sootoo.com"]
    #  开始爬取的地址  按照行业分类来爬取

    base_url = "http://www.sootoo.com/{tag}/{num}/?day=--&page={page}"
    news_types = [
        {"name": "13", "value": "电商"},
        {"name": "204", "value": "o2o"},
        {"name": "18", "value": "游戏"},
        {"name": "86", "value": "it"},
        {"name": "3979", "value": "物联网"},  # keyword
        {"name": "206", "value": "智能硬件"},
        {"name": "24", "value": "移动互联网"}
    ]

    def __init__(self, *a, **kw):
        super(SootooSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_types:
            if news_type.get("value") == "物联网":
                yield Request(
                    self.base_url.format(tag="keyword", num=news_type.get("name"), page=1),
                    meta=news_type,
                    dont_filter=True
                )
            else:
                yield Request(
                    self.base_url.format(tag="tag", num=news_type.get("name"), page=1),
                    meta=news_type,
                    dont_filter=True
                )

    def parse(self, response):
        data_list = response.xpath('//div[@class="ZXGX"]/ul/li')
        if data_list is not None:
            for data in data_list:
                datail_url = data.xpath('./h3/a/@href').extract_first()
                yield Request(
                    datail_url,
                    meta=response.meta,
                    callback=self.detail
                )
        # 获取下一页的数据

    def detail(self, response):
        pass
