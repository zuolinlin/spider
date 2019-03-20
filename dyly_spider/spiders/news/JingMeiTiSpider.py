# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import date_util, RegExUtil


class JingMeiTiSpider(NewsSpider):
    """
    鲸媒体
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "jingmeiti_news"
    allowed_domains = ["jingmeiti.com"]

    news_type_list = [
        {"code": "news", "name": "资讯"},
        {"code": "行业研究", "name": "行业研究"},
        {"code": "elite", "name": "公司报道"},
    ]

    start_url = "http://www.jingmeiti.com/archives/category/{news_type}"

    def __init__(self, *a, **kw):
        super(JingMeiTiSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.start_url.format(news_type=news_type.get("code")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        # if "page" not in response.url:
        #     pages = int(response.xpath('//*[@id="page-content"]/div/div/div[1]/nav/div/*[last()-1]/text()').extract_first())
        #     for page in range(2, pages+1):
        #         yield Request(
        #             self.start_url.format(news_type=response.meta.get("code"))+"/page/{}".format(page),
        #             meta=response.meta,
        #             dont_filter=True
        #         )
        items = response.xpath('//*[@class="posts-default-box"]')
        for item in items:
            push_date = item.xpath("normalize-space(div[2]/div[2]/ul/li[@class='ico-time']/text())").extract_first()
            if "小时前" in push_date:
                push_date = date_util.date_before_h(int(RegExUtil.find_first(r"\d", push_date)))
            detail_url = item.xpath("normalize-space(div[1]/h2/a/@href)").extract_first()
            response.meta.update({
                "out_id": RegExUtil.find_first("/(\d+)$", detail_url),
                "title": item.xpath("normalize-space(div[1]/h2/a/text())").extract_first(),
                "digest": item.xpath("normalize-space(div[2]/div[1]/text())").extract_first(),
                "source": item.xpath("normalize-space(div[2]/div[2]/ul/li[@class='postoriginal']/span/text())").extract_first(),
                "push_date": push_date
            })
            yield Request(
                detail_url,
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        source = response.meta.get("source")
        if "原创文章".__eq__(source) or len(source) == 0:
            source = "鲸媒体"
        self.insert_new(
            response.meta.get("out_id"),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("name"),
            source,
            response.meta.get("digest"),
            response.xpath('//*[@id="page-content"]/div/div/div[1]/div[2]/div[2]/*[position()>1]'),
            response.url,
            16
        )
