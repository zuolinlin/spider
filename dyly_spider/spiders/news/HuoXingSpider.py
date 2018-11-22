# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import date_util


class HuoXingSpider(NewsSpider):
    """
    火星财经
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "huoxing24_news"
    allowed_domains = ["huoxing24.com"]

    news_type_list = [
        {"code": 14, "name": "币市"},
        {"code": 17, "name": "政策"},
        {"code": 2, "name": "公司"},
        {"code": 6, "name": "技术"},
        {"code": 15, "name": "投研"},
    ]

    start_url = "https://www.huoxing24.com/info/news/shownews?currentPage={page}&pageSize=20&channelId={" \
                "news_type}&refreshTime={refresh_time}"
    detail_url = "https://www.huoxing24.com/newsdetail/{out_id}.html"

    def __init__(self, *a, **kw):
        super(HuoXingSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            page = 1
            news_type.update({"page": page})
            yield Request(
                self.start_url.format(page=page, news_type=news_type.get("code"), refresh_time=""),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        obj = self.get_data(response)
        items = obj.get("inforList", [])
        if len(items) > 0:
            # 分页
            page = response.meta.get("page")+1
            response.meta.update({"page": page})
            yield Request(
                self.start_url.format(page=page, news_type=response.meta.get("code"),
                                      refresh_time=items[-1].get("publishTime")),
                meta=response.meta,
                dont_filter=True
            )
            for item in items:
                out_id = item.get("id")
                response.meta.update({
                    "out_id": out_id,
                    "title": item.get("title"),
                    "source": item.get("source"),
                    "push_date": date_util.get_date(item.get("publishTime")),
                    "new_type": response.meta.get("name"),
                    "digest": item.get("synopsis")
                })
                yield Request(
                    self.detail_url.format(out_id=out_id),
                    meta=response.meta,
                    dont_filter=True,
                    callback=self.detail
                )

    def detail(self, response):
        self.insert_new(
            response.meta.get("out_id"),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("new_type"),
            response.meta.get("source"),
            response.meta.get("digest"),
            "".join(response.xpath('//*[@id="detailBox"]/div[@class="detail-text-cont simditor-body"]/*/*')[1:-1].xpath('normalize-space(string(.))').extract()).replace("　", ""),
            14
        )

    def get_data(self, req):
        body = json.loads(req.body)
        if body["code"] == 1:
            return body.get("obj", {})
        else:
            self.log_error("request failed：" + repr(body))

