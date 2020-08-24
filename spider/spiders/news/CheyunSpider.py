import json
import time

from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider

"""
车云：资讯（电动汽车，自动驾驶，智能网联，技术升级，未来出行，人工智能，零售模式，新兴制造，创新创业，全球热点 ）

"""


class CheyunSpider(NewsSpider):

    name = "cheyun_news"

    allowed_domains=["cheyun.com"]

    news_type_list = [
        {"category_index": 1, "name": "电动汽车"},
        {"category_index": 2, "name": "自动驾驶"},
        {"category_index": 3, "name": "智能网联"},
        {"category_index": 4, "name": "技术升级"},
        {"category_index": 5, "name": "未来出行"},
        {"category_index": 6, "name": "人工智能"},
        {"category_index": 7, "name": "零售模式"},
        {"category_index": 8, "name": "新兴制造"},
        {"category_index": 9, "name": "创新创业"},
        {"category_index": 10, "name": "全球热点"},
    ]

    #数据列表
    list_url = "https://openapi.cheyun.com/article/list/{category_index}/0/{page}/30"

    #数据详情
    detail_url = "https://openapi.cheyun.com/article/{id}"

    def __init__(self, *a, **kw):
        super(CheyunSpider, self).__init__(*a, **kw)

    def start_requests(self):
        page = 1
        for news_type in self.news_type_list:
            news_type.update({"page": page})
            yield Request(
                self.list_url.format(page=page, category_index=news_type.get("category_index")),
                meta=news_type,
                dont_filter=True,
                callback=self.parse
            )

    def parse(self, response):
        data_list = response.text
        data_list = json.loads(data_list)
        datas = data_list["data"]["list"]
        if datas is not None and len(datas) != 0:
            for data in datas:
                yield Request(
                    self.detail_url.format(id=data['id']),
                    meta=response.meta,
                    callback=self.detail
                )
        else:
            return

    def detail(self, response):

        data_list = response.text
        data_list = json.loads(data_list)
        data = data_list["data"]

        inputtime = data['inputtime']
        timeArray = time.localtime(inputtime)
        push_date = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
        out_id = data['id']
        title = data['title']
        new_type = response.meta['name']
        source = '车云'
        digest = data["description"]
        content = data["content"]
        source_url = response.url
        spider_source = 112

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





