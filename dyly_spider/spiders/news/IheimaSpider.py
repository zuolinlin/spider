import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class IheimaSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "iheima"
    allowed_domains = ["iheima.com"]
    # 金融与科技
    start_urls = ["http://www.iheima.com/scope/1"
                  ]

    def __init__(self, *a, **kw):
        super(IheimaSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        url = "http://www.ebrun.com/top/1"
        yield Request(
                url=url,
                meta={"selenium": True}
            )

    def parse(self, response):
        html =response.text
        htmls =str_to_selector(html)
        data_list =response.xpath('//div[@class="item-wrap clearfix"]')
        for data in data_list:
            title = data.xpath('./div[@class="desc distable-cell"]/a/text()').extract_first()
            print(title)
