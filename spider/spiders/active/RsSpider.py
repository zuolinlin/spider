
from spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy

"""
全景网=====路演
"""


class RsSpider(ActiveSpider):
    name = "rs_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["p5w.net"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://rs.p5w.net/roadshow/getRoadshowList.shtml'
    base_url = "http://rs.p5w.net/"

    def __init__(self, *a, **kw):
        super(RsSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.start_urls,
            formdata={
                "perComType": "0",
                "page": "0",
                "rows": "12"},
            meta={"page": "0"},
            callback=self.parse
        )

    def parse(self, response):
        data_list = response.text
        datas_json = json.loads(data_list)
        datas = datas_json['rows']
        if datas is not None and len(datas) != 0:
            for data in datas:
                title = data['roadshowTitle']
                url = data['roadshowUrl']
                link = self.base_url +url
                times = data['roadshowDate']
                tags = data['roadshowTypeName']
                source = "全景网"
                self.insert_new(
                    title,
                    times,
                    None,
                    tags,
                    None,
                    link,
                    source
                )
            # page =response.meta['page']
            # next_page = int(page) + 1
            # if next_page <= 1818:
            #     yield scrapy.FormRequest(
            #         url=self.start_urls,
            #         formdata={
            #             "perComType": "0",
            #             "page": str(next_page),
            #             "rows": "12"},
            #         meta={"page": str(next_page)},
            #         callback=self.parse
            #     )

        else:
            return
