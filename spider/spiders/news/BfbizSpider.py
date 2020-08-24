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
不凡商业
"""


class BfbizSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "bfbiz"
    allowed_domains = ["bufanbiz.com"]
    # 最新
    start_urls = ["https://www.bufanbiz.com/api/website/articles/?p=1&n=50&type="
                  ]
    base_detialUrl ="https://www.bufanbiz.com/post/"

    def __init__(self, *a, **kw):
        super(BfbizSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['data']
            for item in items:
                out_id = item['uid']
                title = item['title']
                digest = item['intro']
                source = item['source']
                times = item['time']
                new_type = item['article_type']
                yield Request(
                    url=BfbizSpider.base_detialUrl + str(out_id) + ".html",
                    meta={
                        "out_id": out_id,
                        "title": title,
                        "digest": digest,
                        "source": source,
                        "times": times,
                        "new_type": new_type},
                    callback=self.detail
                )
            # # 请求下一页
            # time.sleep(3)
            # pages = 2
            # while self.current_page < pages:
            #     self.current_page += 1
            #     next_url = "https://www.bufanbiz.com/api/website/articles/?p="+str(self.current_page)+"&n=500&type="
            #     yield Request(next_url, callback=self.parse)

    def detail(self, response):
        out_id = response.meta['out_id']
        title = response.meta['title']
        digest = response.meta['digest']
        source = response.meta['source']
        push_time = response.meta['times']
        new_type = response.meta['new_type']
        content = response.xpath('//div[@class="content-detail"]').extract_first()
        spider_source = 25

        # print(out_id, title, digest, source, push_time, new_type, content)
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
