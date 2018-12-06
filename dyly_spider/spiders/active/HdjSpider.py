import time
from scrapy import Request
import urllib.parse
import uuid

from dyly_spider.spiders.BaseSpider import BaseSpider

class HdjSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdj_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["huodongjia.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['https://www.huodongjia.com/finance/page-1/']

    def __init__(self, *a, **kw):
        super(HdjSpider, self).__init__(*a, **kw)
    base_url ="https://www.huodongjia.com"

    def parse(self, response):
        data_list = response.xpath('//div[@class="all_events"]/div[@class="eventList"]')
        if data_list is not None:
            for data in data_list:
                title = data.xpath('./div/h3/a/text()').extract_first()
                link = data.xpath('./div/h3/a/@href').extract_first()
                link = self.base_url+link
                times = data.xpath('./div/p[@class="address"][1]/text()').get().strip()
                place = data.xpath('./div/p[@class="address"][1]/a/text()').extract_first()
                source = "活动家"
                classify= "金融财经"
                tags_data = data.xpath('./div/p[@class="meeting_tags"]//a//text()').extract()
                tags = ""
                if tags_data is not None and len(tags_data) != 0:
                    for i, tag in enumerate(tags_data):
                        tags += tag
                        if i != len(tags_data) - 1:
                            tags = tags + "、"
                # 插入sql
                pojo = self.fetchone(
                    "SELECT 1 FROM `financial_activities_bak` WHERE `link`='%s' AND `source`='%s' " % (
                    link, source)
                )
                if pojo is None:
                    self.insert("""
                                                          INSERT INTO `financial_activities_bak` (
                                                            `id`,
                                                            `title`,
                                                            `time`,
                                                            `place`,
                                                            `tag`,
                                                            `classify`,
                                                            `link`,
                                                            `source`,
                                                            `createTime`
    
                                                          ) 
                                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                                          """, (
                        str(uuid.uuid4()).replace("-", ""),
                        title,
                        times,
                        place,
                        tags,
                        classify,
                        link,
                        source,
                        time.localtime()
                    ))
            next_url= response.xpath('//div[@class="pagination"]/ul/li[last()]/a/@href').extract_first()
            if next_url is not None:
                next_url = self.base_url+next_url
                # yield Request(next_url, callback=self.parse)
                yield Request(next_url, dont_filter=True, callback=self.parse)

            else:
                return
