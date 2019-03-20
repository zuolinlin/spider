# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider


class PencilNewsSpider(NewsSpider):
    """
    铅笔道
    """

    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 1
    # }

    name = "pencilnews_news"

    news_type_list = [
        {"code": "1", "name": "圈内热点"},
        {"code": "2", "name": "早期项目"},
        {"code": "16", "name": "区块链"},
        {"code": "3", "name": "深度"},
        {"code": "15", "name": "投资人"},
    ]

    list_url = "https://api.pencilnews.cn/articles?page={page}&page_size=20&cate_id={news_type}"
    detail_url = "https://www.pencilnews.cn/p/{out_id}.html?from=article_list"

    def __init__(self, *a, **kw):
        super(PencilNewsSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=0),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        data = self.get_data(response)
        articles = data.get("articles", [])
        for article in articles:
            article_info = article.get("article_info", {})
            out_id = article_info.get("article_id")
            response.meta.update({
                "out_id": out_id,
                "push_date": article_info.get("create_at"),
                "title": article_info.get("title"),
                "digest": article_info.get("digest"),
            })
            yield Request(
                self.detail_url.format(out_id=out_id),
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )
        # 分页
        # page = data.get("_pageinfo").get("page")
        # if page == 0:
        #     pages = data.get("_pageinfo").get("pages")+1
        #     for page in range(1, pages):
        #         yield Request(
        #             self.list_url.format(news_type=response.meta.get("code"), page=page),
        #             meta=response.meta,
        #             dont_filter=True
        #         )

    def detail(self, response):
        self.insert_new(
            response.meta.get("out_id"),
            response.meta.get("push_date"),
            response.meta.get("title"),
            response.meta.get("name"),
            "铅笔道",
            response.meta.get("digest"),
            response.xpath("//div[@class='article_content']"),
            response.url,
            38
        )

    def get_data(self, req):
        body = json.loads(req.body)
        if body["code"] == 1000:
            return body["data"]
        else:
            self.log_error("request failed：" + repr(body))
