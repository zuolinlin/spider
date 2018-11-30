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
    news_type_url_list = [
        {
            "code": "https://cn.technode.com/post/category/startups/",
            "name": "初创公司报道"},
        {
            "code": "https://cn.technode.com/post/category/technode-talks/",
            "name": "观点"},
        {
            "code": "https://cn.technode.com/post/category/blockchain/",
            "name": "区块链"},

    ]

    def start_requests(self):
        for news_url in self.news_type_url_list:
            yield Request(
                news_url["code"],
                dont_filter=True
            )

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
            new_url = response.url
            urls = str(new_url).split("/")
            new_types = urls[5]
            if new_types == "startups":
                new_type = "初创公司报道"
            elif new_types == "technode-talks":
                new_type = "观点"
            elif new_types == "blockchain":
                new_type = "区块链"
            yield Request(
                url,
                meta={"content": content,
                      "new_type": new_type},
                callback=self.detail
            )
        # 请求下一页
        next_url = response.xpath('//div[@class="page-nav"]/a[last()]/@href').get()
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
        new_type = response.meta['new_type']
        # 来源
        source = "动点科技"
        #  摘要
        digest = response.meta['content']
        # 内容
        content = response.xpath('//article/p').extract()
        content = "".join(content)
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
            response.url,
            spider_source
        )
