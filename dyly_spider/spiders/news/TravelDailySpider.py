# -*- coding: utf-8 -*-

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil, date_util


class TravelDailySpider(NewsSpider):
    """
    环球旅讯
    """

    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 1
    # }

    name = "traveldaily_news"

    news_type_list = [
        {"code": "online", "name": "在线旅游"},
        {"code": "hotel", "name": "酒店"},
        {"code": "investment", "name": "投资并购"},
        {"code": "tech", "name": "旅游科技"},
    ]

    domain = "https://www.traveldaily.cn"

    list_url = "https://www.traveldaily.cn/{news_type}/{page}/"

    def __init__(self, *a, **kw):
        super(TravelDailySpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=1),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        items = response.xpath('//*[@id="mainlist"]/li')
        for item in items:
            detail_url = self.domain + item.xpath('div[2]/h2/a/@href').extract_first()
            push_date = item.xpath('normalize-space(div[2]/div/text())').extract_first()
            if "小时前" in push_date:
                push_date = date_util.date_before_h(int(RegExUtil.find_first(r"\d+", push_date)))
            elif "昨天" in push_date:
                push_date = date_util.get_before_date_str(1)+" "+RegExUtil.find_first(r"\d+:\d+", push_date)
            response.meta.update({
                "out_id": RegExUtil.find_first("/(\d+)", detail_url),
                "title": item.xpath('normalize-space(div[2]/h2/a/text())').extract_first(),
                "push_date": push_date,
                "digest": item.xpath('normalize-space(div[2]/p/a/text())').extract_first(),
            })
            yield Request(
                detail_url,
                meta=response.meta,
                dont_filter=True,
                priority=1,
                callback=self.detail
            )
        # 分页
        cur_page = int(response.xpath("/html/body/div[4]/div[2]/div[2]/span[1]/a[@class='active']/text()").extract_first())
        if cur_page == 1:
            pages = int(response.xpath('//*[@id="pibox"]/@data-max').extract_first())
            for page in range(2, pages+1):
                yield Request(
                    self.list_url.format(news_type=response.meta.get("code"), page=page),
                    meta=response.meta,
                    dont_filter=True
                )

    def detail(self, response):
        self.insert_new(
            response.meta.get("out_id"),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("name"),
            response.xpath('normalize-space(//*[@id="article"]/div[2]/div[1]/div[2]/p/span'
                           '[@class="article-soy"]/text())').extract_first()[3:],
            response.meta.get("digest"),
            response.xpath('//*[@id="article"]/div[2]/div[1]/div[@class="article-content"]'),
            response.url,
            34
        )
