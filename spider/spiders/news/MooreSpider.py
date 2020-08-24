from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json

"""
  摩尔芯球
"""

class MooreSpider(NewsSpider):
    start_urls = ["https://moore.live/"]
    name = "moore_news"
    allowed_domains = ["moore.com"]
    news_type_url_list = [
        {"code": "https://moore.live/news/api/list/1/?page=1&per_page=20&recommend=true",
         "name": "芯热门"},
        {"code": "https://moore.live/news/api/list/14/?page=1&per_page=20&recommend=None",
         "name": "芯科技"},
        {"code": "https://moore.live/news/api/list/10/?page=1&per_page=20&recommend=None",
         "name": "芯设计"},
        {"code": "https://moore.live/news/api/list/11/?page=1&per_page=20&recommend=None",
         "name": "芯制造"},
        {"code": "https://moore.live/news/api/list/12/?page=1&per_page=20&recommend=None",
         "name": "芯材料"},
        {"code": "https://moore.live/news/api/list/13/?page=1&per_page=20&recommend=None",
         "name": "芯封测"},
        {"code": "https://moore.live/news/api/list/15/?page=1&per_page=20&recommend=None",
         "name": "芯财报"},
        {"code": "https://moore.live/news/api/list/16/?page=1&per_page=20&recommend=None",
         "name": "芯情报"},
    ]
    def start_requests(self):
        for news_url in self.news_type_url_list:
            yield Request(
                news_url["code"],
                dont_filter=True
            )

    def __init__(self, *a, **kw):
        super(MooreSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def parse(self, response):
        datas = json.loads(response.text)
        data_json = datas["data"]['rows']
        for data in data_json:
            title = data['news']['title']
            conver_url = data['news']['headImg']
            id = data['news']['id']
            detail_url ="https://moore.live/news/"+str(id)+"/detail/"
            yield Request(
                url=detail_url,
                meta={"id": id,
                      "title": title,
                      "conver_url": conver_url},
                dont_filter=True,
                callback=self.detail

            )

    def detail(self, response):
        # out_id =response.meta.get('id')
        id = response.meta.get('id')
        cover = response.meta.get('conver_url')
        title = response.meta.get('title')
        published_at = response.xpath('//div[@class="origin"]/p[@class="otherinfo"]/span[3]/text()').extract_first()

        content = response.xpath(
            "/html/body").extract_first(),
        new_type = "半导体、芯片",

        # print(id,
        #     published_at,
        #     title,
        #     new_type,
        #     "摩尔芯球",
        #     None,
        #     content,
        #     response.url,
        #     "102",
        #     cover)

        self.insert_new(
            id,
            published_at,
            title,
            new_type,
            "摩尔芯球",
            None,
            content,
            response.url,
            102
        )

        # self.insert_new_1(
        #     id,
        #     published_at,
        #     title,
        #     new_type,
        #     "摩尔芯球",
        #     None,
        #     content,
        #     response.url,
        #     "102",
        #     cover
        # )
        pass

