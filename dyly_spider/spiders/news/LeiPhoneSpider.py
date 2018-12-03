# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class LeiPhoneSpider(NewsSpider):
    """
    雷锋网
    """

    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 1
    # }

    name = "leiphone_news"

    news_type_list = [
        {"code": "ai", "name": "人工智能"},
        {"code": "transportation", "name": "智能驾驶"},
        {"code": "aijuejinzhi", "name": "AI+"},
        {"code": "fintech", "name": "Fintech&区块链"},
        {"code": "aihealth", "name": "未来医疗"},
        {"code": "letshome", "name": "网络安全"},
        {"code": "arvr", "name": "AR/VR"},
        {"code": "robot", "name": "机器人"},
        {"code": "yanxishe", "name": "开发者"},
        {"code": "weiwu", "name": "智能硬件"},
        {"code": "iot", "name": "物联网"},
    ]

    list_url = "https://www.leiphone.com/category/{news_type}/page/{page}"

    def __init__(self, *a, **kw):
        super(LeiPhoneSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            news_type.update({"page": 1})
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=news_type.get("page")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        items = response.xpath("/html/body/div[3]/div/div[1]/div[2]/div/ul/li")
        for item in items:
            detail_url = item.xpath("div/div[2]/h3/a/@href").extract_first()
            out_id = "-".join(RegExUtil.find_first("news/(.+?)/(.+?).html", detail_url))
            response.meta.update({
                "out_id": out_id,
                "title": item.xpath("normalize-space(div/div[2]/h3/a/text())").extract_first(),
                "source": "雷锋网",
                "digest": item.xpath("normalize-space(div/div[2]/div[1]/text())").extract_first(),
            })
            yield Request(
                detail_url,
                meta=response.meta,
                dont_filter=True,
                priority=1,
                callback=self.detail
            )
        # 分页
        cur_page = int(response.xpath("/html/body/div[3]/div/div[1]/div[2]/div/div/div/span[@class='cur']/text()").extract_first())
        if cur_page == 1:
            pages = int(response.xpath("/html/body/div[3]/div/div[1]/div[2]/div/div/div/a[last()]/text()").extract_first())
            for page in range(2, pages+1):
                yield Request(
                    self.list_url.format(news_type=response.meta.get("code"), page=page),
                    meta=response.meta,
                    dont_filter=True
                )

    def detail(self, response):
        detail = response.xpath("//div[@class='article-template']")
        self.insert_new(
            response.meta.get("out_id"),
            detail.xpath("normalize-space(div[1]/div/div[1]/table/tr/td[@class='time']/text())").extract_first(),
            response.meta.get("title"),
            response.meta.get("name"),
            response.meta.get("source"),
            response.meta.get("digest"),
            detail.xpath("div[2]/div/div[1]/div[@class='lph-article-comView']"),
            response.url,
            32
        )
