# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider


class JieMoDuiSpider(NewsSpider):
    """
    芥末堆
    """

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 1
    }

    name = "jiemodui_news"

    news_type_list = [
        {"code": 54, "name": "观察"},
        {"code": 51, "name": "深度"},
        {"code": 52, "name": "产品"},
        {"code": 49, "name": "政策"},
        {"code": 57, "name": "资本"},
        {"code": 53, "name": "栏目"},
    ]

    list_url = "https://www.jiemodui.com/Home/EditCate/getRelNews?cateId={news_type}&page={page}"
    detail_url = "https://www.jiemodui.com/{item_type}/{out_id}.html"

    def __init__(self, *a, **kw):
        super(JieMoDuiSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            news_type.update({"page": 1})
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=news_type.get("page")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        data = self.get_data(response)
        if data is not None and len(data) > 0:
            page = response.meta.get("page")+1
            response.meta.update({"page": page})
            yield Request(
                self.list_url.format(news_type=response.meta.get("code"), page=page),
                meta=response.meta,
                dont_filter=True,
            )
            for item in data:
                out_id = item.get("id")
                response.meta.update({
                    "out_id": out_id,
                    "push_date": item.get("rPtime"),
                    "title": item.get("name"),
                    "source": item.get("writer"),
                    "digest": item.get("brief"),
                })
                yield Request(
                    self.detail_url.format(item_type=item.get("item_type"), out_id=out_id),
                    meta=response.meta,
                    dont_filter=True,
                    priority=1,
                    callback=self.detail
                )

    def detail(self, response):
        self.insert_new(
            response.meta.get("out_id"),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("name"),
            response.meta.get("source"),
            response.meta.get("digest"),
            response.xpath('//*[@id="Read"]'),
            response.url,
            30
        )

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == '000':
            return data["list"]
        else:
            self.log_error("request failed：" + repr(data))
