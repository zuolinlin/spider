from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import time
import scrapy

"""
36氪  ===近期活动
"""


class KrSpider(ActiveSpider):
    name = "kr_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["36kr.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://chuang.36kr.com/api/actapply?page={pageNo}&pageSize=12'

    def __init__(self, *a, **kw):
        super(KrSpider, self).__init__(*a, **kw)

    def start_requests(self):
       yield Request(
            self.start_urls.format(pageNo=1),
            dont_filter=True
        )

    def parse(self, response):
        text = response.text
        data_list = json.loads(text)
        datas = data_list['data']['data']
        if datas is not None or len(datas) != 0:
            for data in datas:
                title = data['title']
                link = data['link']
                place = data['city']
                times = data['activityBeginTime']
                times = str(times)[0:10]
                timeArray = time.localtime(int(times))
                times = time.strftime("%Y-%m-%d", timeArray)
                classify = '创业服务'
                source = "36氪"
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
        # totalPages = data_list['data']['totalPages']
        # page = data_list['data']['page']
        # next_page= int(page)+1
        # if next_page <= totalPages:
        #     yield Request(
        #         self.start_urls.format(pageNo=next_page),
        #         dont_filter=True
        #     )
        else:
            return
