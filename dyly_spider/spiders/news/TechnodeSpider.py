# -*- coding: utf-8 -*-
import json
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
初创公司  观点  区块链
"""
class TechnodeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "technode_news"
    allowed_domains = ["cn.technode.com"]
    news_type_list = [
        {"code": 1, "name": "初创公司报道"},
        # {"code": 2, "name": "观点"},
        # {"code": 3, "name": "区块链"},
        # {"code": 4, "name": "NodeBang"},
        # {"code": 5, "name": "科技快讯"},
    ]

    start_urls = [#"https://cn.technode.com/post/category/startups/"       # 初创公司报道
                 # "https://cn.technode.com/post/category/technode-talks/",  # 观点
                  "https://cn.technode.com/post/category/blockchain/",      # 区块链
                 #  "https://cn.technode.com/nodebang/",                      # nodebang
                 #  "https://cn.technode.com/newsnow/"                       # 科技快讯
                  ]

    def __init__(self, *a, **kw):
        super(TechnodeSpider, self).__init__(*a, **kw)
        self.browser =None

    def parse(self, response):
        data_list = response.xpath('//*[@id="inner-wrap"]/div[5]/div/div/div/div/div/div[1]/div[@class="td_mod_wrap td_mod9 "]')
        for data in data_list:
            #  新闻详情页URl
            url = data.xpath('.//div[@class="item-details"]/h3/a/@href').get().strip()
            # 摘要
            content = data.xpath('.//div[@class="item-details"]/p/text()').get().strip()
            yield Request(
                url,
                meta={"content": content},
                callback=self.detail
            )
        # 请求下一页
        next_url =response.xpath('//div[@class="page-nav"]/a[last()]/@href').get()
        if not next_url:
            return
        else:
            yield Request(next_url, callback=self.parse)

    #
    def detail(self, response):
        # 外部编号
        url = response.url
        splits = str(url).split('/')
        out_id = splits[4] + splits[5]
        # 标题
        title = response.xpath('//h1[@class="entry-title"]/text()').get().strip()
        # 时间
        push_time = response.xpath('//time[@itemprop="dateCreated"]/text()').get().strip()
        # 新闻类型
        new_type = "区块链"
        # 来源
        source = "动点科技"
        #  摘要
        digest = response.meta['content']
        # 内容
        content = response.xpath('//article//p//text()').getall()
        content = "".join(content).strip()
        # 爬取来源
        spider_source = 3
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
