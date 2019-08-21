import scrapy

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request
import json
from util import date_util
import time

class ItjuziSpider(NewsSpider):
    name = "itjuzi_news"
    allowed_domains = ["itjuzi.com"]

    # news_type_url_list = [
    #     {"code": "https://www.itjuzi.com/news#selected"},
    #     {"code": "https://www.itjuzi.com/news#invst"},
    #     {"code": "https://www.itjuzi.com/news#grasp"},
    # ]

    def __init__(self, *a, **kw):
        super(ItjuziSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        url = 'https://www.itjuzi.com/api/news'

        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url=url,
            formdata={"page": "1", "per_page": "100"},
            callback=self.parse_page
        )

    def parse_page(self, response):
        datas =json.loads(response.body.decode('utf-8'));
        data_json = datas["data"]["data"]
        for data in data_json:
            id =data['id']
            title = data['title']
            publishTime = data['time']
            newsType = data['news_type']
            mainUrl = data['main_url']
            url = data['url']
            yield Request(
                url,
                meta={"id": id,
                      "title": title,
                      "publishTime": publishTime,
                      "newsType": newsType,
                      "mainUrl": mainUrl
                      },
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        content = response.xpath("/html/body").extract_first()
        title = response.meta["title"]
        timeStamp = response.meta["publishTime"]
        timeArray = time.localtime(timeStamp)
        publishTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
       # publishTime =date_util.strptime(str(response.meta["publishTime"]), "%Y-%m-%d %H:%M:%S"),
        new_type = response.meta["newsType"]
        out_id =response.meta["id"]
        source = "it桔子"
        spider_source = 41
        self.insert_new(
            out_id,
            publishTime,
            title,
            new_type,
            source,
            None,
            content,
            response.url,
            spider_source
        )
        pass