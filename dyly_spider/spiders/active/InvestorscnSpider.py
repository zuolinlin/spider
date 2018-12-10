from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy
"""
投资家 ==== 活动
"""


class InvestorscnSpider(ActiveSpider):
    name = "investorscn_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["thecapital.com.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['http://www.investorscn.com/activity/p1/']

    def __init__(self, *a, **kw):
        super(InvestorscnSpider, self).__init__(*a, **kw)

    def parse(self, response):
        data_list = response.xpath('//div[@class="hd-list"]/ul/li')
        if data_list is not None:
            for data in data_list:
                link = data.xpath('./div[@class="con"]/a/@href').extract_first()
                title = data.xpath('./div[@class="con"]/a/text()').extract_first()
                classify = data.xpath('./div[@class="con"]/div[@class="des"]/a/text()').extract_first()
                times = data.xpath('./div[@class="con"]/div[@class="des"]/text()[4]').extract_first()
                times = str(times)[3:].split(" _ ")[0]
                times = str(times).replace(r'年-', '-').replace(r'月-', '-').replace(r'日', ' ')
                place = data.xpath('./div[@class="con"]/div[@class="des"]/text()[3]').extract_first()
                place = str(place)[3:]
                source = "投资家"
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )
        next_url = response.xpath('//div[@class="page-list "]/a[last()]/@href').extract_first()
        if next_url is not None:
            yield Request(
                next_url,
                dont_filter=True,
                callback=self.parse
            )
        else:
            return 
