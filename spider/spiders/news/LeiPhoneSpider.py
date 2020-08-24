# -*- coding: utf-8 -*-

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
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
        items = response.xpath("//html/body//div[@class='list']//div[@class='word']")

        for item in items:

            detail_url = item.xpath("h3/a/@href").extract_first()

            out_id = "-".join(RegExUtil.find_first("news/(.+?)/(.+?).html", detail_url))
            response.meta.update({
                "out_id": out_id.strip(),
                "title": item.xpath(".//h3/a/text()").extract_first(),
                "source": "雷锋网",
                "digest": item.xpath(".//div[1]/text()").extract_first(),
            })
            yield Request(
                detail_url,
                meta=response.meta,
                dont_filter=True,
                priority=1,
                callback=self.detail
            )

        # 分页
        # 取消注释可爬取全部内容（有反爬，建议每次爬一页）
        # cur_page = int(response.xpath("//html/body//div[@class='list']//div[@class='pages']/span[@class='cur']/text()").extract_first())
        # print(cur_page)
        # if cur_page == 1:
        #     pages = int(response.xpath("//html/body//div[@class='list']//div[contains(@class, 'pages')]/a[5]/text()").extract_first())
        #     print(pages)
        #
        #     for page in range(2, pages+1):
        #         yield Request(
        #             self.list_url.format(news_type=response.meta.get("code"), page=page),
        #             meta=response.meta,
        #             dont_filter=True
        #         )

    def detail(self, response):
        # detail = response.xpath("//div[@class='article-template']")

        # print(
        #     response.meta.get("out_id"),
        #     detail.xpath("//td[contains(@class, 'time')]/text()").extract_first(),
        #     response.meta.get("title"),
        #     response.meta.get("name"),
        #     response.meta.get("source"),
        #     response.meta.get("digest"),
        #     # detail.xpath("/html/body").extract_first(),
        #     response.url,
        #     32
        # )
        content = response.xpath("/html/body").extract_first(),
        if content is None:
            pass
        else:
            self.insert_new(
                response.meta.get("out_id"),
                response.xpath("//td[contains(@class, 'time')]/text()").extract_first().strip(),
                response.meta.get("title"),
                response.meta.get("name"),
                response.meta.get("source"),
                response.meta.get("digest"),
                content,
                response.url,
                32
            )
