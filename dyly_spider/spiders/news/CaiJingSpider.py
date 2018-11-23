# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class CsSpider(NewsSpider):
    """
    零壹财经
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "caijing_news"
    allowed_domains = ["01caijing.com"]

    news_type_list = [
        {"code": 1010, "name": "互联网+"},
        {"code": 1016, "name": "消费金融"},
        {"code": 1054, "name": "上市公司"},
        {"code": 1053, "name": "银行科技"},
    ]

    list_url = "https://www.01caijing.com/articles_loading.json?pageIndex={page}&pageSize=10&categoryId={news_type}"

    def __init__(self, *a, **kw):
        super(CsSpider, self).__init__(*a, **kw)

    def start_requests(self):
        page = 1
        for news_type in self.news_type_list:
            news_type.update({"page": page})
            yield Request(
                self.list_url.format(page=page, news_type=news_type.get("code")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        items = response.xpath("/html/body/div[@class='single-article']")
        # 下一页
        if len(items) > 0:
            page = response.meta.get("page")+1
            response.meta.update({"page": page})
            yield Request(
                self.list_url.format(page=page, news_type=response.meta.get("code")),
                meta=response.meta,
                dont_filter=True
            )
        for item in items:
            response.meta.update({
                "digest": item.xpath("normalize-space(div/div/p/text())").extract_first(),
                "source": RegExUtil.find_first("(.*) ·", item.xpath("normalize-space(div/div/small/text())")
                                               .extract_first())
            })
            yield Request(
                "http://" + item.xpath("div/div/h2/a/@href").extract_first()[2:].replace("ejinrong", "article"),
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        detail = response.xpath("/html/body/div[2]/div[1]/div[2]")
        self.insert_new(
            RegExUtil.find_first(r"/(\d+?).htm", response.url),
            detail.xpath("normalize-space(small/span[2]/text())").extract_first(),
            detail.xpath("normalize-space(h1/text())").extract_first(),
            response.meta.get("name"),
            response.meta.get("source"),
            response.meta.get("digest"),
            "".join(detail.xpath("div[@class='article-txt']").xpath('normalize-space(string(.))').extract()).replace('　', ''),
            10
        )
