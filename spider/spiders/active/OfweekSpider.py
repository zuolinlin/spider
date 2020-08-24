from spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy

"""
OFweek维科网  === 行业会议
"""


class OfweekSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "ofweek_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["ofweek.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['https://seminar.ofweek.com/INDEXMTList-ABO-1.html']

    def parse(self, response):
        text = response.text
        text = text[10:-1]
        json_text = json.loads(text)
        if json_text is not None and len(json_text) != 0:
            for page in json_text:
                title = page['seminarName']
                times = page['seminarTime']
                place = page['address']
                link = page['htmlpath']
                source = "维科网"
                self.insert_new(
                        title,
                        times,
                        place,
                        None,
                        None,
                        link,
                        source
                                )
