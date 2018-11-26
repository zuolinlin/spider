# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import date_util, XPathUtil


class ChinaVentureSpider(NewsSpider):
    """
    投资中国
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "chinaventure_news"
    allowed_domains = ["chinaventure.com.cn"]

    news_type_list = [
        {"code": 11, "name": "VC/PE"},
        {"code": 3, "name": "瞰三板"},
        {"code": 20, "name": "产业资本"},
        {"code": 14, "name": "锐公司"},
        {"code": 5, "name": "金融"},
        {"code": 4, "name": "潮汛Hot"},
        {"code": 23, "name": "人物"},
        {"code": 2, "name": "原创"},
    ]

    start_url = "https://www.chinaventure.com.cn/cmsmodel/news/jsonListByChannel/{news_type}/{offset}-{page_size}.shtml"

    def __init__(self, *a, **kw):
        super(ChinaVentureSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            news_type.update({
                "offset": 0
            })
            yield Request(
                self.start_url.format(news_type=news_type.get("code"), offset=0, page_size=12),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        # 分页
        data = self.get_data(response)
        if data is not None:
            items = data.get("list", [])
            if len(items) > 0:
                offset = response.meta.get("offset")
                offset = offset + 12 if offset == 0 else offset + 10
                response.meta.update({"offset": offset})
                yield Request(
                    self.start_url.format(news_type=response.meta.get("code"), offset=offset, page_size=10),
                    meta=response.meta,
                    dont_filter=True
                )
            for item in items:
                new = item.get("news")
                out_id = new.get("id")
                self.insert_new(
                    out_id,
                    date_util.get_date(new.get("publishAt")),
                    new.get("title"),
                    response.meta.get("name"),
                    new.get("srcName"),
                    new.get("introduction"),
                    new.get("content"),  # XPathUtil.str_to_selector(new.get("content")),
                    "https://www.chinaventure.com.cn/cmsmodel/news/detail/{out_id}.shtml".format(out_id=out_id),
                    26
                )

    def get_data(self, req):
        body = json.loads(req.body)
        if body["status"] == 100000:
            return body["data"]
        else:
            self.log_error("request failed：" + repr(body))
