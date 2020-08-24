import json
import time

from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider

"""
极客公园：极客之选，产品观察，极客出行，顶楼TopView，Intelligence Plus，挖App，图赏，极客指南

"""


class GeekparkSpider(NewsSpider):
    name = "geekpark_news"

    allowed_domains=["geekpark.net"]

    start_url = "http://www.geekpark.net"

    news_type_list = [
        {"category_code": 81, "name": "极客之选"},
        {"category_code": 85, "name": "产品观察"},
        {"category_code": 250, "name": "极客出行"},
        {"category_code": 177, "name": "顶楼TopView"},
        {"category_code": 261, "name": "Intelligence Plus"},
        {"category_code": 170, "name": "挖App"},
        {"category_code": 251, "name": "图赏"},
        {"category_code": 91, "name": "极客指南"}
    ]

    # 数据列表
    list_url = "https://mainssl.geekpark.net/api/v1/columns/{category_code}?page={page}"

    # 数据详情
    detail_url = "http://www.geekpark.net/news/{id}"

    def __init__(self, *a, **kw):
        super(GeekparkSpider, self).__init__(*a, **kw)

    def start_requests(self):
        page = 1
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(page=page, category_code=news_type.get("category_code")),
                meta=news_type,
                dont_filter=True,
                callback=self.parse
            )

    def parse(self, response):
        data_list = response.text
        data_list = json.loads(data_list)
        datas = data_list["column"]["posts"]
        if datas is not None and len(datas) != 0:
            for data in datas:
                yield Request(
                    self.detail_url.format(id=data['id']),
                    meta={
                        "title": data['title'],
                        "digest": data['abstract'],
                        "out_id": data['id'],
                        "new_type": response.meta['name'],
                        "published_timestamp": data['published_timestamp']
                    },
                    callback=self.detail
                )
        else:
            return

    def detail(self, response):

        out_id = response.meta['out_id']
        title = response.meta['title']
        digest = response.meta['digest']
        new_type = response.meta['new_type']
        source = '极客公园'
        source_url = response.url
        spider_source = 106

        published_timestamp = response.meta['published_timestamp']
        timeArray = time.localtime(published_timestamp)
        push_date = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)

        content = response.xpath('//div[@class="article-content"]').extract_first()

        # print(out_id, push_date, title, new_type, source, digest, source_url, spider_source)
        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )