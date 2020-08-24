from spider.spiders.BaseSpider import BaseSpider
import json
from scrapy import Request
import uuid


class BaikeDictSpider(BaseSpider):
    name = "baike_dict"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["baike.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://fenlei.baike.com/{classifyName}/list/'

    def __init__(self, *a, **kw):
        super(BaikeDictSpider, self).__init__(*a, **kw)

    def start_requests(self):
        datas = self.fetchall("SELECT  classify_name FROM `xsbbiz`.`baike_classify` GROUP BY classify_name ")
        for data in datas:
            className = data[0]
            yield Request(
                self.start_urls.format(classifyName=className),
                meta={
                    "className": str(className)
                }
            )

    def parse(self, response):
        data_list = response.xpath('//dl[@class="link_blue line-25 zoom"]/dd')
        for data in data_list:
            dict = data.xpath('./a/text()').extract_first()
            className = response.meta['className']
            params = []
            params.append((
                className,
                dict
            ))
            self.insert("""
                                           INSERT INTO `baike_classify_dict` (
                                             `classify_name`,
                                             `dict`
                                           )
                                           VALUES (%s, %s)
                                           """, params)
