# -*- coding: utf-8 -*-

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
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
            pages = int(response.xpath("//html//div[@class='container']//div[@class='pager']/a[last()-1]/text()").extract_first()) #总页数

            for page in range(2, 3):       # 若需爬全部新闻，则改为range(2, pages)
                yield Request(
                    self.start_url.format(news_type=response.meta.get("code"), page=page),
                    meta=response.meta,
                    dont_filter=True
                )
        items = response.xpath("//html/body//div[@class='list-post']/div[@class='post-item']")

        for item in items:
            url = item.xpath(".//div[contains(@class, 'post-main')]/div[contains(@class, 'post-inner')]/a/@href").extract_first()
            title = item.xpath(".//div[contains(@class, 'post-main')]/div[contains(@class, 'post-inner')]/a[contains(@class, 'post-title')]/text()").extract_first()
            digest = item.xpath(".//div[contains(@class, 'post-main')]/div[contains(@class, 'post-inner')]/p[contains(@class, 'post-desc')]/text()").extract_first()

            response.meta.update({
                                    "title": title,
                                    "digest": digest
            })
            yield Request(
                url,
                meta = response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):

        out_id =  RegExUtil.find_first(r"/(\d+?).shtml", response.url).strip()

        # push_time = response.xpath("//html/body//div[contains(@class, 'subject-meta')]").extract_first().split('发布')[0]
        detail = response.xpath("//html/body//div[contains(@class, 'subject-meta')]/text()").extract_first().split('发布')
        push_time = detail[0].strip()

        title = response.meta['title']
        new_type = response.meta['name']
        source = RegExUtil.find_first("来源：(.+?) \\xa0", detail[1].strip())
        digest = response.meta['digest']
        content = response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 12

        # print(out_id, push_time,title, new_type,source,digest,source_url,spider_source)

        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )
