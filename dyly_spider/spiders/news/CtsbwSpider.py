import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from dyly_spider.spiders.news.NewsSpider import NewsSpider

class CtsbwSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "ctsbw"
    allowed_domains = ["ctsbw.com"]
    # 金融与科技
    start_urls = ["http://www.ctsbw.com/cn"
                  ]

    def __init__(self, *a, **kw):
        super(CtsbwSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = response.xpath('//ul[@class="content news-photo picbig"]/article')
        if data_list is not None and len(data_list):
            for data in data_list:
                #  url
                url = data.xpath('./div/div/div/div/div/h4/a/@href').get()\
                    .strip()
                out_id = url[29:-5]
                yield Request(url, meta={"out_id": out_id},callback=self.detail)
            # 只能请求到190 页的数据，后面的分页数据不对
            pages = 190
            while self.current_page < pages:
                  self.current_page += 1
                  next_url = "http://www.ctsbw.com/cn/" + str(self.current_page)+".html"
                  yield Request(next_url, callback=self.parse)

    def detail(self, response):
        out_id = response.meta['out_id']
        #  详情页模版一
        crumbs_one = response.xpath('//div[@class="cj_content"]/div[@class="crumbs"]')
        if crumbs_one is not None and len(crumbs_one) != 0:
           title = response.xpath('//div[@class="cj_content"]/h2/text()').get().strip()  # 标题
           push_time = response.xpath('//p[@class="fa s14"]/text()[2]').get().strip()  # 时间
           source = response.xpath('//p[@class="fa s14"]/span[4]/text()').get().strip()  # 来源
           source = str(source).split('：')[1]
           digest = response.xpath('//div[@class="cj_content"]/div[3]/p/text()').get().strip()  # 摘要
           content =response.xpath('//div[@class="para_ycont"]/div[@class=" col-xs-12"][1]//p//text()').getall()
           content = "".join(content).strip()
           new_type = "国内"
           spider_source = 11
        # 详情页模版二
        crumbs_two = response.xpath('//div[@class="cj_content"]/div[@class="cj_laiyuan fa s14"]/div[@class="crumbs"]')
        if crumbs_two is not None and len(crumbs_two):
            title = response.xpath('//div[@class="cj_content"]/div[1]/div/h2/text()').get().strip()  # 标题
            push_time = response.xpath('//div[@class="cj_content"]/div[1]/div/p/text()[2]').get().strip()  # 时间
            source = response.xpath('//div[@class="cj_content"]/div[1]/div/p/span[2]/text()').get().strip()  # 来源
            source = str(source).split('：')[1]
            digest = response.xpath('//div[@class="cj_content"]/div[2]/div[2]/p/text()').get().strip()  # 摘要
            content = response.xpath('//div[@class="para_ycont"]/div[@class=" col-xs-12"][1]//p//text()').getall()
            content = "".join(content).strip()
            new_type = "国内"
            spider_source = 11

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