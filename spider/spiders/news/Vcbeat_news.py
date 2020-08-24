
from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import scrapy
import json
import time

"""
  动脉网
"""
class Vcbeat_news(NewsSpider):
    name = "vcbeat_news"
    allowed_domains = ["vcbeat.top"]

    # news_type_url_list = [
    #     {"code": "https://www.itjuzi.com/news#selected"},
    #     {"code": "https://www.itjuzi.com/news#invst"},
    #     {"code": "https://www.itjuzi.com/news#grasp"},
    # ]

    def __init__(self, *a, **kw):
        super(Vcbeat_news, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        url = 'https://vcbeat.top/index.php/Index/Index/ajaxGetArticleList'

        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url=url,
            formdata={"page": "1"},
            callback=self.parse_page
        )

    def parse_page(self, response):
        datas = json.loads(response.text)
        data_json = datas["data"]
        for data in data_json:
            uid = data['uid']
            title = data['title']
            logo_path = data['logo_path']
            logo_path ="https://cdn.vcbeat.top"+str(logo_path)
            newsType = "医疗健康"
            url = "https://vcbeat.top/"+data['detail_id']

            yield Request(
                url,
                meta={"id": uid,
                      "title": title,
                      "conver_image":logo_path,

                      "newsType": newsType
                      },
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        content = response.xpath("/html/body").extract_first()
        title = response.meta["title"]
        conver_image = response.meta["conver_image"]
        new_type = response.meta["newsType"]
        out_id = response.meta["id"]
        source = "动脉网"
        spider_source = 101
        publishTime = response.xpath('//div[@class="atr_info clear"]/span[@class="time"]/text()').extract_first()
        # print(
        #     out_id,
        #     publishTime,
        #     title,
        #     new_type,
        #     source,
        #     None,
        #     content,
        #     response.url,
        #     spider_source,
        #     conver_image
        # )

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
        # self.insert_new_1(
        #     out_id,
        #     publishTime,
        #     title,
        #     new_type,
        #     source,
        #     None,
        #     content,
        #     response.url,
        #     spider_source,
        #     conver_image
        # )
        pass