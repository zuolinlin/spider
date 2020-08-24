from spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request, FormRequest
import time
import scrapy
"""
虎嗅网  ==   虎嗅网
"""


class HuxiuSpider(ActiveSpider):
    name = "huxiu_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["huxiu.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.huxiu.com/active/more'
    base_url = "https://www.huxiu.com/"

    def __init__(self, *a, **kw):
        super(HuxiuSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield FormRequest(
            self.start_urls,
            formdata={"huxiu_hash_code": "b896a56653e8668bd192fc05f3cb80b7",
                      "is_ajax": '1',
                      "page": "1"
                      },
            meta={"page": "1"},
            callback=self.parse

        )

    def parse(self, response):
        data_json = json.loads(response.text)
        datas = data_json['data']
        if datas is not None and len(datas) != 0:
            for data in datas:
                title = data['title']
                place = data['address']
                link = data['link']
                times = data['date']
                classify = "活动"
                source = "虎嗅网"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )
                # 取当前页的数据即可
                # page = response.meta["page"]
                # next_page = int(page) + 1
                # yield FormRequest(
                #     self.start_urls,
                #     formdata={"huxiu_hash_code": "b896a56653e8668bd192fc05f3cb80b7",
                #               "is_ajax": '1',
                #               "page": str(next_page)
                #               },
                #     meta={"page": str(next_page)},
                #     callback=self.parse
                #
                # )

