# -*- coding: utf-8 -*-
import re
import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from spider.spiders.news.NewsSpider import NewsSpider

"""
 新浪= 金融新闻
"""


class SinaSpider(NewsSpider):

    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "sina_news"
    allowed_domains = ["sina.com.cn"]
    # 最新
    start_urls = ["http://feed.mix.sina.com.cn/api/roll/get?pageid=155&lid=1690&num=10&page={n}&callback=feedCardJsonpCallback&_=1584670170529"
                      .format(n = n) for n in range(1, 2)
                  ]

    def __init__(self, *a, **kw):
        super(SinaSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(
                start_url,
                callback=self.parse
            )

    def parse(self, response):
        datas = response.text
        datas = re.findall(r'try{feedCardJsonpCallback\((.*?)\);}catch\(e\){};', datas)
        datas = datas[0].encode('utf-8')
        datas_json = json.loads(datas.decode('utf-8'));

        data_list = datas_json['result']['data']
        for data in data_list:
            out_id = data['oid']
            # push_time = data['ctime']

            push_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(data['ctime'])))

            print(push_time)
            title = data['title']
            new_type = '金融新闻'
            digest = data['summary']
            detail_url = data['url']

            # print(detail_url)
            yield Request(
                detail_url,
                meta={
                    "out_id": out_id,
                    "push_time": push_time,
                    "title": title,
                    "new_type": new_type,
                    "digest": digest,
                },
                callback=self.detail
            )


    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        title = response.meta['title']
        new_type = response.meta['new_type']

        source = response.xpath("//a[contains(@class, 'source ent-source')]/text()").extract_first()
        if source is None:
            source = response.xpath("//span[contains(@class, 'source ent-source')]/text()").extract_first()


        digest = response.meta['digest']
        content = response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 37


        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     source_url,
        #     spider_source
        # )

        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )



