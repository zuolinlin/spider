from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import time
import scrapy
"""
创客猫=====创客活动
"""


class ChuangkemSpider(ActiveSpider):
    name = "chuangkem_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["chuangkem.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['http://www.chuangkem.com/chuangkehuodong']
    base_url = "http://www.chuangkem.com"

    def __init__(self, *a, **kw):
        super(ChuangkemSpider, self).__init__(*a, **kw)

    def parse(self, response):
        data_list = response.xpath('//div[@class="activity-list clearfix mt30"]/div[@class="item"]')
        for data in data_list:
            title = data.xpath('./div[@class="text"]/h3/a/text()').extract_first()
            link = data.xpath('./div[@class="text"]/h3/a/@href').extract_first()
            link = self.base_url+ link
            place = data.xpath('./div[@class="text"]/ul/li[@class="li1"]/text()').extract_first()
            times = data.xpath('./div[@class="text"]/ul/li[@class="li2"]/text()').extract_first()
            classify = "创客活动"
            source = "创客猫"
            self.insert_new(
                title,
                times,
                place,
                None,
                classify,
                link,
                source
            )
        # 获取一下页的数据
        # next_url = response.xpath('//div[@class="pagination text-center"]/ul/li[last()]/a/@href').extract_first()
        # last_url = response.xpath('//div[@class="pagination text-center"]/ul/li[last() -1]/a/@href').extract_first()
        # if next_url == last_url:
        #     return
        # else:
        #     next_url = self.base_url + next_url
        #     yield Request(
        #         next_url,
        #         callback=self.parse
        #     )
