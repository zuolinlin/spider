# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class YouXiTuoLuoSpider(NewsSpider):
    """
    游戏陀螺
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "youxituoluo_news"

    list_url = "https://www.youxituoluo.com/cms/mg.php?r=alltype/listmore&tp=news&page={page}"
    domain = "https://www.youxituoluo.com"

    def __init__(self, *a, **kw):
        super(YouXiTuoLuoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.list_url.format(page=1),
            meta={"page": 1},
            dont_filter=True
        )

    def parse(self, response):
        items = response.xpath("//div[@class='article']")
        if len(items) > 0:
            for item in items:
                yield Request(
                    self.domain + item.xpath("div[2]/h1/a/@href").extract_first(),
                    meta={
                        "title": item.xpath("normalize-space(div[2]/h1/a/text())").extract_first(),
                        "digest": item.xpath("normalize-space(div[2]/p[2]/text())").extract_first(),
                        "push_date": item.xpath("normalize-space(div[2]/p[1]/text())").extract_first(),
                    },
                    dont_filter=True,
                    priority=1,
                    callback=self.detail
                )
            page = response.meta.get("page")+1
            yield Request(
                self.list_url.format(page=page),
                meta={"page": 1},
                dont_filter=True
            )

    def detail(self, response):
        # self.log((
        #     RegExUtil.find_first("/(\d+).html", response.url),
        #     response.meta.get("push_date"),
        #     response.meta.get("title"),
        #     "游戏资讯",
        #     "游戏陀螺",
        #     response.meta.get("digest"),
        #     response.xpath("//div[@class='info_p']"),
        #     response.url,
        # ))
        self.insert_new(
            RegExUtil.find_first("/(\d+).html", response.url),
            response.meta.get("push_date"),
            response.meta.get("title"),
            "游戏资讯",
            "游戏陀螺",
            response.meta.get("digest"),
            response.xpath("//div[@class='info_p']"),
            response.url,
            46
        )

