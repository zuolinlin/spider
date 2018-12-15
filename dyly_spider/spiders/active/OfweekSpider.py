from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
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
    start_urls = ['https://seminar.ofweek.com/']

    def parse(self, response):
        title = response.xpath('//*[@id="hmeeting"]/div/dl/dt/a/text()').extract_first()
        text = response.xpath('//*[@id="hmeeting"]/div/dl/dd[1]/span/text()').extract_first()

