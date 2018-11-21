# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class DuoZhiSpider(NewsSpider):
    """
    多知网
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "duozhi_news"
    allowed_domains = ["duozhi.com"]

    news_type_list = [
        {"code": "industry", "name": "产业"},
        {"code": "company", "name": "公司"},
    ]

    start_url = "http://www.duozhi.com/{news_type}/{page}.shtml"
    detail_url = "http://www.duozhi.com/{news_type}/{out_id}.shtml"

    def __init__(self, *a, **kw):
        super(DuoZhiSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.start_url.format(news_type=news_type.get("code"), page="index"),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        # 分页
        if "index.shtml" in response.url:
            pages = int(response.xpath("/html/body/div[1]/div[1]/div[4]/div[1]/div[5]/a[last()-1]/text()").extract_first())
            for page in range(2, pages+1):
                yield Request(
                    self.start_url.format(news_type=response.meta.get("code"), page=page),
                    meta=response.meta,
                    dont_filter=True
                )
        items = response.xpath("/html/body/div[1]/div[1]/div[4]/div[1]/div[4]/div")
        for items in items:
            response.meta.update({
                "digest": items.xpath("normalize-space(div[2]/div[2]/p/text())").extract_first()
            })
            yield Request(
                items.xpath("h3/a/@href").extract_first(),
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        detail = response.xpath("/html/body/div[1]/div[1]/div[3]/div[1]/div")
        self.insert_new(
            RegExUtil.find_first(r"/(\d+?).shtml", response.url),
            detail.xpath("normalize-space(div[1]/span/text())").extract_first()[0:-2],
            detail.xpath("normalize-space(h1/text())").extract_first(),
            response.meta.get("name"),
            RegExUtil.find_first("来源：(.+?)\\t", detail.xpath("div[1]/text()")[1].get().strip()),
            response.meta.get("digest"),
            "".join(detail.xpath("div[@class='subject-content']").xpath('normalize-space(string(.))').extract()).replace("　", ""),
            12
        )
