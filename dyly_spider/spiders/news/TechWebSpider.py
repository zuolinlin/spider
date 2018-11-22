# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import date_util, RegExUtil


class TechWebSpider(NewsSpider):
    """
    techweb
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "techweb_news"
    allowed_domains = ["techweb.com.cn"]

    start_url = "http://www.techweb.com.cn/finance/list_{page}.shtml"

    def __init__(self, *a, **kw):
        super(TechWebSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_url.format(page=1),
            dont_filter=True
        )

    def parse(self, response):
        # 分页
        page = RegExUtil.find_first("/list_(\d+).shtml", response.url)
        if int(page) == 1:
            pages = int(RegExUtil.find_first("/list_(\d+).shtml", response.xpath("/html/body/div[3]/div[1]/div["
                                                                                 "3]/div[16]/a[last("
                                                                                 ")]/@href").extract_first()))
            for url in [self.start_url.format(page=page) for page in range(2, pages+1)]:
                yield Request(
                    url,
                    dont_filter=True
                )
        items = response.xpath("/html/body/div[3]/div[1]/div[3]/div[position()<last()]")
        for item in items:
            yield Request(
                item.xpath("div[1]/a/@href").extract_first(),
                dont_filter=True,
                callback=self.detail
            )
            # self.log(item.xpath("normalize-space(div[1]/a/h4/text())").extract_first())

    def detail(self, response):
        source = response.xpath("normalize-space(/html/body/div[5]/div[1]/div[1]/div[1]/span[2]/a/text())").extract_first()
        if "TechWeb.com.cn".__eq__(source):
            source = "TechWeb"
        self.insert_new(
            RegExUtil.find_first("/(\d+).shtml", response.url),
            response.xpath("normalize-space(/html/body/div[5]/div[1]/div[1]/div[1]/span[1]/text())").extract_first(),
            response.xpath("normalize-space(/html/body/div[5]/div[1]/h1/text())").extract_first(),
            "财经",
            source,
            None,
            "".join(response.xpath('//*[@id="content"]').xpath('normalize-space(string(.))')
                    .extract()).replace("　", ""),
            18
        )
