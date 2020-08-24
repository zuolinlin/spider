# -*- coding: utf-8 -*-
from urllib.parse import unquote

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil, date_util


class TobSheSpider(NewsSpider):
    """
    拓扑社
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "tobshe_news"
    allowed_domains = ["itjuzi.com"]

    start_urls = ["https://tobshe.itjuzi.com/category/tobviewpoint/"]

    def __init__(self, *a, **kw):
        super(TobSheSpider, self).__init__(*a, **kw)

    def parse(self, response):
        # 分页
        url = response.xpath('//*[@id="next-posts"]/a/@href').extract_first()
        if url is not None:
            yield Request(
                url,
                dont_filter=True
            )
        items = response.xpath('//div[@class="col-sm-12"]')
        for item in items:
            yield Request(
                item.xpath("div/div/h4/a/@href").extract_first(),
                dont_filter=True,
                meta={
                    "title": item.xpath("normalize-space(div/div/h4/a/text())").extract_first(),
                    "push_date": item.xpath("normalize-space(div/div/small/text())").extract_first(),
                    "digest": item.xpath("normalize-space(div/div/p/text())").extract_first()
                },
                callback=self.detail
            )

    def detail(self, response):
        out_id = "_".join(RegExUtil.find_first("tobshe.itjuzi.com/(.+)/(.+)/(.+)/(.+)/$", unquote(response.url, 'utf-8')))

        print(
            out_id,
            date_util.strptime(response.meta.get("push_date"), "%Y年%m月%d日"),
            response.meta.get("title"),
            "拓·灼见",
            "拓扑社",
            response.meta.get("digest"),
            # response.xpath('//div[@class="post-content"]'),
            response.url,
            24
        )
        # self.insert_new(
        #     out_id,
        #     date_util.strptime(response.meta.get("push_date"), "%Y年%m月%d日"),
        #     response.meta.get("title"),
        #     "拓·灼见",
        #     "拓扑社",
        #     response.meta.get("digest"),
        #     response.xpath('//div[@class="post-content"]'),
        #     response.url,
        #     24
        # )
