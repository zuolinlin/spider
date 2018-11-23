# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class XtecherSpider(NewsSpider):
    """
    Xtecher
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "xtecher_news"
    allowed_domains = ["xtecher.com"]

    start_url = "http://xtecher.com/Website/Article/index?cat=0&page={page}"

    def __init__(self, *a, **kw):
        super(XtecherSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_url.format(page=1),
            dont_filter=True
        )

    def parse(self, response):
        # 分页
        page = int(RegExUtil.find_first("page=(\d+)", response.url))
        if page == 1:
            pages = int(response.xpath('//*[@id="featureContent"]/div[2]/div[3]/a[last()-1]/text()').extract_first())
            for page in range(2, pages+1):
                yield Request(
                    self.start_url.format(page=page),
                    dont_filter=True
                )
        items = response.xpath('//li[@class="contentBox"]/div[2]')
        for item in items:
            yield Request(
                "http://xtecher.com"+item.xpath('a/@href').extract_first(),
                dont_filter=True,
                meta={
                    "title": item.xpath('normalize-space(a/h4/text())').extract_first(),
                    "source": item.xpath('normalize-space(div[1]/p/text())').extract_first().replace("来源：", ""),
                    "push_date": item.xpath('normalize-space(div[3]/p/text())').extract_first()
                },
                callback=self.detail
            )

    def detail(self, response):
        self.insert_new(
            RegExUtil.find_first("aid=(\d+)", response.url),
            response.meta.get("push_date"),
            response.meta.get("title"),
            "资讯",
            response.meta.get("source"),
            None,
            "".join(response.xpath('//div[@class="content_box feature_content"]/div/*[position()<last()]')
                    .xpath('normalize-space(string(.))').extract()).replace("　", ""),
            22
        )
