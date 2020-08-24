# -*- coding: utf-8 -*-
import json
import time
from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class YouXiTuoLuoSpider(NewsSpider):
    """
    游戏陀螺
    """
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 1
    }

    name = "youxituoluo_news"

    base_url = 'https://www.youxituoluo.com/'
    start_urls = ["https://www.youxituoluo.com/api/post/category/list?page={n}&limit=15&slug=news".format(n = n ) for n in range(1, 2)]

    def __init__(self, *a, **kw):
        super(YouXiTuoLuoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(
                start_url
            )

    def parse(self, response):
        datas = json.loads(response.body.decode('utf-8'))
        data_json = datas['data']['data']

        for data in data_json:
            out_id = data['aid']
            push_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['sendtime']))
            title = data['title']
            news_type = '游戏资讯'
            source = '游戏陀螺'
            digest = data['dis']
            content = data['content']
            detail_url = self.base_url + str(out_id) + '.html'

            yield Request(
                detail_url,
                meta = {
                    'out_id': out_id,
                    'push_time': push_time,
                    'title': title,
                    'news_type': news_type,
                    'source': source,
                    'digest': digest,
                    'content': content,
                    'detail_url': detail_url
                },
                callback=self.detail
            )

        pass

    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        title = response.meta['title']
        news_type = response.meta['news_type']
        source = response.meta['source']
        digest =response.meta['digest']
        content = response.meta['content']
        detail_url = response.meta['detail_url']
        spider_source = 46
        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     news_type,
        #     source,
        #     digest,
        #     content,
        #     detail_url,
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
            detail_url,
            spider_source
        )

