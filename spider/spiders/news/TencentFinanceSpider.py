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
腾讯财经新闻
"""


class TencentFinanceSpider(NewsSpider):


    name = "tencent_finance_news"
    allowed_domains = ["new.qq.com"]
    # 最新
    start_urls = ["https://pacaio.match.qq.com/irs/rcd?cid=135&token=6e92c215fb08afa901ac31eca115a34f&callback=jspnphotnews&ext=finance&page={n}&num=15&expIds=20200323A0CD3E|20200323014121|20200323A0478V|20200323A0FUE9|20200323004242|20200123A0EGGC|20200120A077K9&callback=jspnphotnews"
                      .format(n = n) for n in range(0, 5)
                  ]

    def __init__(self, *a, **kw):
        super(TencentFinanceSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def start_requests(self):
        headers = {
            'Referer':'https://new.qq.com/ch/finance/',
            'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'
        }
        for start_url in self.start_urls:
            yield Request(
                start_url,
                dont_filter = True,
                headers=headers
            )

    def parse(self, response):
        datas = response.text
        datas = re.findall(r'jspnphotnews\((.*?)\)', datas)[0]
        try:
            datas = json.loads(datas)
        except Exception as e:
            datas += "\",\"publish_time\":0,\"title\":0,\"source\":0,\"vurl\":0}]}"
            datas = json.loads(datas)
            data_json = datas['data'][:-1]
            print(data_json)
        else:
            data_json= datas['data']


        # datas = json.loads(datas)
        # data_json = datas['data']

        # print(datas)


        for item in data_json:
            out_id = item['app_id']
            push_time = item['publish_time']
            title = item['title']
            news_type = '财经'
            # source = item['source']
            source = '腾讯财经'
            digest = item['intro']
            detail_url = item['vurl']

            yield Request(
                detail_url,
                meta={
                    'out_id': out_id,
                    'push_time': push_time,
                    'title': title,
                    'news_type': news_type,
                    'source': source,
                    'digest': digest
                },
                callback=self.detail
            )


    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.meta['push_time']
        title = response.meta['title']
        news_type = response.meta['news_type']
        source = response.meta['source']
        digest = response.meta['digest']
        content = response.xpath('/html/body').extract_first()
        source_url = response.url
        spider_source = 61

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