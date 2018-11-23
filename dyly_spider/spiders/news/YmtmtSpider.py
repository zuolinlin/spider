import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
一鸣网
"""


class YmtmtSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "ymtmt"
    allowed_domains = ["ymtmt.com"]
    # 最新
    start_urls = ["http://www.ymtmt.com/news/index/index/page/1.html"
                  ]
    base_url = "http://www.ymtmt.com"

    def __init__(self, *a, **kw):
        super(YmtmtSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = response.xpath('//div[@class="xw-li"]')
        if data_list is not None:
            for data in data_list:
                url = data.xpath('./div[@class="right"]/h1/a/@href').extract_first()  # url
                url = YmtmtSpider.base_url + url
                yield Request(
                        url,
                        callback=self.detail
                )
            time.sleep(5)
            # 获取下一页的数据
            pages = 701
            while self.current_page < pages:
                self.current_page += 1
                next_url = "http://www.ymtmt.com/news/index/index/page/" + str(self.current_page)+".html"
                yield Request(next_url,  callback=self.parse)

    def detail(self, response):
        url = response.url
        out_id =str(url)[42:-5] #
        title = response.xpath('//span[@class="nn1"]/text()').extract_first()  # 标题
        digest = response.xpath('//div/div[@class="sp-xq wz-ny bnt1"]/div[@class="left zb-n"]/p[@class="gy"]/text()').extract_first() # 摘要
        new_type = response.xpath('/html/body/div/div[2]/div/div[1]/dl/dd/span[3]/a/text()').extract_first()   # 新闻类型
        push_time = response.xpath('///span[@class="nn2"]/text()').extract_first()   # 新闻时间
        push_time = str(push_time).split("  |  ")[1].split("                          ")[0]

        source = "一鸣网"  # 新闻来源
        content = response.xpath('//div[@class="sp-xq wz-ny bnt1"]/div[@class="left zb-n"]//p//text()').getall()  # 新闻内容
        content = "".join(content).strip()
        content = content.split("-END-")[0]
        spider_source = 21
        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            spider_source
        )
