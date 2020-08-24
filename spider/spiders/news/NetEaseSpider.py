# -*- coding: utf-8 -*-
import re
import json
import time

from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider

"""
初创公司  观点  区块链
"""


class NetEaseSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "netEase_news"
    allowed_domains = ["163.com"]

    # start_urls = ["http://money.163.com/special/00253368/institutions.html"]

    news_type_list = [
        {'name': '基金', 'code': 'fund'},
        {'name': '商业', 'code': 'biz'},
        {'name': '股票', 'code': 'stock'}
    ]
    start_urls = 'https://money.163.com/special/00259BVP/news_flow_{news_type}{page}.js?callback=data_callback'

    def __init__(self, *a, **kw):
        super(NetEaseSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def start_requests(self):
        for news_type in self.news_type_list:
            news_type.update({'page': ''})
            yield Request(
                self.start_urls.format(news_type=news_type.get('code'), page=news_type.get('page')),
                meta = news_type,
                dont_filter=True
            )

    def parse(self, response):
        data = response.body.decode('gbk')
        data = '{"' + data[:13] + '":' + data[14:-1] + '}'
        data = json.loads(data)['data_callback']

        for item in data:
            title = item['title']
            push_time = item['time']

            timeArray = time.strptime(push_time, "%m/%d/%Y %H:%M:%S")
            timestamp = time.mktime(timeArray)
            push_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

            news_type = response.meta['name']
            source = '网易财经'
            digest = item['digest']
            detail_url = item['docurl']

            # out_id = re.findall(r'\d{4}/\d{2}/(.*?)\.html', detail_url)[0]
            out_id = detail_url[-21:-5]

            yield Request(
                detail_url,
                meta={
                    'out_id': out_id,
                    'title': title,
                    'push_time': push_time,
                    'news_type': news_type,
                    'source': source,
                    'digest': digest
                },
                callback=self.detail
            )

        # # 分页
        # while self.current_page < 9:
        #     self.current_page += 1
        #
        #     response.meta.update({'page': '_0'+str(self.current_page)})
        #     next_url = self.start_urls.format(news_type=response.meta.get('code'), page=response.meta.get('page'))
        #     yield Request(
        #         next_url,
        #         meta=response.meta,
        #         dont_filter=True
        #     )

    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        title = response.meta['title']
        news_type = response.meta['news_type']
        source = response.meta['source']
        digest = response.meta['digest']
        content = response.xpath('/html/body').extract_first()
        source_url = response.url
        spider_source = 36

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     news_type,
        #     source,
        #     digest,
        #     # content,
        #     source_url,
        #     spider_source
        # )

        self.insert_new(
            out_id,
            push_time,
            title,
            news_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )
