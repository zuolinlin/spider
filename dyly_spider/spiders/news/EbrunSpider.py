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
亿邦动力
"""


class EbrunSpider(NewsSpider):

    """
     重新设置请求头的信息
    """
    custom_settings = {
        "COOKIES_ENABLED": False,
        'DEFAULT_REQUEST_HEADERS': {
            'Cookie':'_iebrunUu=1542786776533*2072011462*201055142; _ebrunUu=1542786776538*541074929*1742710736; UM_distinctid=1673541fe66caf-0eeab5dc75a804-35607400-1aeaa0-1673541fe6749f; Hm_lvt_87daad7faca22f66ec178d201d855ddb=1542786777; __adcookie=1543799744045*695075063*636685350; sso_token_wwwebruncom=c8a22s7qexkcggk4g80og80cs; _iebrunUv=1543799745067*878476387*1555295442; _ebrunUv=1543799745070*1648279599*973533719; _Jo0OQK=4BD8B136271943F46897B751A001B307789E1E4E7E07210315B153FAE6550ABF882E76EA2FDF5F4AE4D427D0A161E780487E6EF31FF37C1BD0FA17EBBF306E8E7F56898A6F0B3D4D4AF126BD1FCCD4B8A12126BD1FCCD4B8A126AB3FC5C314C7605GJ1Z1KA==; XSRF-TOKEN=eyJpdiI6IjhvazI4TEJLTURPQU4xdERXYnZkUWc9PSIsInZhbHVlIjoiQVhYbWoyZ3krUFVQWXlcL05la0I0VWd5ckVHeVFiakg3dysrVFFzeXdtUVVBNk9oZUFOMWRtOFBIc0FXYkRmUTh0dzRXN1BoamJjSWozU1BkZGJjU0RBPT0iLCJtYWMiOiJiZjk4NDYxOTlhMDc3MzViNmI3OGQyNDgyYzI4ZWIwOWFjZThlMWQyNGMwZTg4ZjMxOTAwMmY1MWVmMDgwOTgyIn0%3D; laravel_session=eyJpdiI6ImdRSmZiS3dUa3JJSFV1dVNHd3JiUWc9PSIsInZhbHVlIjoiVWFpRWRGajhHWFZRdXNYQWxNQlA0Z3NkY3FOeEwyK25oXC9LZVRYTUxORXFVQnk3T0QxRU0wS0txS0VjZ2JPeW02bENFQ3BrOFFyZFwvUDVFeHFIdUZwUT09IiwibWFjIjoiNjQzZmFjYTYwNjUwMDNkOTYzZDZhYTEyNGIxMTBkYzI3ZDY5OWJmNDc4NjdlYzEzMzFjZmJlOWJmYjAxMTk3OCJ9; CNZZDATA30003236=cnzz_eid%3D321411720-1542784369-http%253A%252F%252Fwww.ebrun.com%252F%26ntime%3D1543800024; Hm_lpvt_87daad7faca22f66ec178d201d855ddb=1543801346'
        }
    }


    name = "ebrun_new"
    allowed_domains = ["ebrun.com"]
    # 最新
    start_urls = ["http://www.ebrun.com/top/1"
                  ]
    cookies = {
        "iebrunUu": "1542786776533*2072011462*201055142",
        "_ebrunUu": "1542786776538*541074929*1742710736"
    }

    def start_requests(self):
        yield Request(
            url="http://www.ebrun.com/top/1",
            cookies=self.cookies,
            callback=self.parse
        )

    def __init__(self, *a, **kw):
        super(EbrunSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def parse(self, response):
            data_list = response.xpath('//div[@data-type="article"]')
            if data_list is not None:
                for data in data_list:
                    title = data.xpath('./a/div[@class="liebiao-well"]/p[@class="liebiao-xinwen-title"]/text()').extract_first()  # 标题
                    cover = data.xpath(
                        './a/div[@class="liebiao-image"]/img/@src').extract_first()
                    url = data.xpath('./a[@acpos="www.ebrun.com_chan_lcol_fylb"]/@href').extract_first()  # url
                    out_id = data.xpath('@data-id').extract_first()
                    push_time = data.xpath('./div[@class="liebiao-xinwen-side"]/p[@class="time"]/text()').extract_first()  # 时间
                    digest = data.xpath('./a/div[@class="liebiao-well"]/p[@class="liebiao-xinwen-des"]/text()').extract_first()  # 摘要
                    yield Request(
                        url,
                        meta={
                            "title": title,
                            "out_id": out_id,
                            "push_time": push_time,
                            "digest": digest,
                            "cover": cover
                        },
                        callback=self.detail

                    )



            # time.sleep(3)
            # # 获取下一页的数据
            # next_url = response.xpath('//li[@class="pagination-next"]/a/@href').extract_first()
            # if str(next_url) == "javascript:void(0)":
            #     return
            # else:
            #     yield Request(next_url, callback=self.parse)

    def detail(self, response):
        title = response.meta['title']
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        digest = response.meta['digest']
        cover = response.meta['cover']
        spider_source = 13
        new_type = "top"

        try:
            source = response.xpath('//article/div/p[@class="source"]/span[2]/text()').extract_first()
            source = str(source).split(": ")[1]
            content = response.xpath('//div[@class="post-text"]').extract_first()
        except:
            source = "亿邦动力"
            try:
                content = response.xpath('//div[@id="pic"]').text
            except:
                content = None
        if content is not None:
            self.insert_new_1(
                out_id,
                push_time,
                title,
                new_type,
                source,
                digest,
                content,
                response.url,
                spider_source,
                cover
            )


