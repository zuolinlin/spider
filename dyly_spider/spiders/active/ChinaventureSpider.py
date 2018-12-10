from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy
"""
投中网  ==活动
"""


class ChinaventureSpider(ActiveSpider):
    name = "chinaventure_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["thecapital.com.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['https://www.chinaventure.com.cn/meet/search/2/2/1/1/0-10.shtml?keyword=&day=&address=&guest=']
    base_url = "https://www.chinaventure.com.cn/"
    next_url = "https://www.chinaventure.com.cn/meet/search/2/2/1/2/{start}-10.shtml?keyword=&day=&address=&guest="

    def __init__(self, *a, **kw):
        super(ChinaventureSpider, self).__init__(*a, **kw)

    def parse(self, response):
        data_list = response.text
        data_list = json.loads(data_list)
        datas = data_list['data']
        if datas is not None or len(datas) != 0:
            for data in datas:
                try:
                    place = data['provinceName']
                    suffer = str(place)[-1:]
                    if place == "中国" or suffer == "省":
                        place = data['cityName']
                except:
                    place = None
                title = data['name']
                times = data['startDateStr']
                link = data['url']
                source = "投中网"
                classify = "行业会议"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )
            url = response.url
            next_url_no = url[52:62]
            next_no = str(next_url_no).split('-')[0]
            next_no = int(next_no) + 10
            yield Request(
                self.next_url.format(start=next_no),
                dont_filter=True,
                callback=self.parse
            )

