
from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy

"""
21财经网=== 品牌论坛
"""


class JingjiSpider(ActiveSpider):
    name = "jingji_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["21jingji.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['https://app.21jingji.com/epaper/html/market.html']

    def __init__(self, *a, **kw):
        super(JingjiSpider, self).__init__(*a, **kw)

    def parse(self, response):
        data_list = response.xpath('//a[@class="Mlist"]')
        for data in data_list:
            link = data.xpath('./@href').extract_first()
            title = data.xpath('./@title').extract_first()
            times = data.xpath('./p/text()').get().strip()
            times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
            place = data.xpath('./p/font/text()').extract_first()
            classify = "品牌论坛"
            source = "21财经"
            self.insert_new(
                title,
                times,
                place,
                None,
                classify,
                link,
                source
            )
