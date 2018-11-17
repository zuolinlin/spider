# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider


class KrSpider(BaseSpider):

    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "36kr_news"
    allowed_domains = ["36kr.com"]

    start_urls = [""]

    def __init__(self, *a, **kw):
        super(KrSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                dont_filter=True
            )

    def parse(self, response):
        """
        机构列表
        :param response:
        :return:
        """
        data = self.get_data(response)
        if data is not None:
            page_data = data["pageData"]

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))


