
from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy

"""
微吼直播   === 直播主页
"""


class VhallSpider(ActiveSpider):
    name = "vhall_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["vhall.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://e.vhall.com/home/user-webinarlist'
    base_url = "http://live.vhall.com/"

    def __init__(self, *a, **kw):
        super(VhallSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.start_urls,
            formdata={
                "user_id": "157024",
                "curr_page": "1",
                "pagesize": "8"},
            meta={"curr_page": "1"},
            callback=self.parse
        )

    def parse(self, response):
        data_text = response.text
        json_data = json.loads(data_text)
        datas = json_data['data']['data']
        if datas is not None and len(datas) != 0:
            for data in datas:
                title = data['subject']
                times = data['start_time']
                id = data['id']
                link = self.base_url+str(id)
                source = "微吼直播"
                self.insert_new(
                    title,
                    times,
                    None,
                    None,
                    None,
                    link,
                    source
                )
            curr_page = response.meta['curr_page']
            next_page = int(curr_page) + 1
            yield scrapy.FormRequest(
                url=self.start_urls,
                formdata={
                    "user_id": "157024",
                    "curr_page": str(next_page),
                    "pagesize": "8"},
                meta={"curr_page": next_page},
                callback=self.parse
            )
        else:
            return
