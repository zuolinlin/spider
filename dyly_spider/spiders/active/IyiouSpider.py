from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import time
import scrapy


"""
亿欧网 ---金融、人工智能、大健康
"""


class IyiouSpider(ActiveSpider):
    name = "iyiou_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["iyiou.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.iyiou.com/activity/getActivityList?page={page}&industry={industry}&city=0'

    def __init__(self, *a, **kw):
        super(IyiouSpider, self).__init__(*a, **kw)

    active_types = [
        {"name": "金融", "value": "4-0"},
        {"name": "人工智能", "value": "93-0"},
        {"name": "活动", "value": "64-0"}
    ]

    def start_requests(self):
        for active_type in self.active_types:
            yield Request(
                    self.start_urls.format(page=1, industry=active_type.get("value")),
                    meta={
                        "name": active_type.get('name'),
                        "value": active_type.get("value"),
                        "page": 1
                    },
                    dont_filter=True
                )

    def parse(self, response):
        text = response.text
        json_text = json.loads(text)
        data_list = json_text['data']
        if data_list is not None:
            for data in data_list:
                title = data['title']
                place = data['city']
                link = data['url']
                date = data['date']
                times = str(date).replace(r'/', '-').replace(r'/', '-')
                classify = response.meta['name']
                source = "亿欧网"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                    )
        else:
            return
        page = response.meta['page']
        next_page = int(page)+1
        yield Request(
            self.start_urls.format(page=next_page, industry=response.meta['value']),
            meta={
                "name": response.meta['name'],
                "value": response.meta["value"],
                "page": next_page
            },
            callback=self.parse
        )



