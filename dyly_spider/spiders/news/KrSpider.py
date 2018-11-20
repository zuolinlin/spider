# -*- coding: utf-8 -*-
import json
import time

from pydispatch import dispatcher
from scrapy import Request, signals
from selenium import webdriver

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import date_util


class KrSpider(NewsSpider):
    """
    36氪
    """

    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "36kr_news"
    allowed_domains = ["36kr.com"]

    news_type_list = [
        {"code": 23, "name": "大公司"},
        {"code": 221, "name": "消费"},
        {"code": 225, "name": "娱乐"},
        {"code": 218, "name": "前沿技术"},
        {"code": 219, "name": "汽车交通"},
        {"code": 208, "name": "区块链"},
        {"code": 103, "name": "技能Get"},
    ]

    list_url = "https://36kr.com/api/search-column/{news_type}?per_page=20&page={page}"
    detail_url = "https://36kr.com/p/{new_id}.html"

    def __init__(self, *a, **kw):
        super(KrSpider, self).__init__(*a, **kw)
        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
                                        chrome_options=chrome_options)
        # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(news_type=news_type.get("code"), page=1),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        data = self.get_data(response)
        if data is not None:
            page = data.get("page")
            if page == 1:
                total_count = data.get("total_count")
                pages = int(total_count / 20) if total_count % 20 == 0 else int(total_count / 20) + 1
                while page < pages:
                    page = page + 1
                    yield Request(
                        self.list_url.format(news_type=response.meta.get("code"), page=page),
                        meta=response.meta,
                        dont_filter=True,
                        callback=self.parse
                    )
            time.sleep(30)
            for item in data.get("items", []):
                out_id = item.get("id")
                push_date = date_util.strptime(item.get("published_at"), '%Y-%m-%dT%H:%M:%S+08:00')
                response.meta.update({"out_id": out_id, "selenium": True, "push_date": push_date})
                yield Request(
                    self.detail_url.format(new_id=out_id),
                    meta=response.meta,
                    dont_filter=True,
                    callback=self.detail
                )

    def detail(self, response):
        out_id = str(response.meta.get("out_id"))
        detail = response.xpath('//*[@id="J_post_wrapper_' + out_id + '"]')
        source = detail.xpath('normalize-space(div[1]/div/div[4]/div/div/div[1]/a/span/text())').extract_first()
        if source is None or len(source) == 0 or "36氪" in source:
            source = "36氪"
        self.insert_new(
            out_id,
            response.meta.get("push_date"),
            detail.xpath('normalize-space(div[1]/h1/text())').extract_first(),
            response.meta.get("name"),
            source,
            detail.xpath('normalize-space(div[1]/div/section[1]/text())').extract_first(),
            "".join(detail.xpath('div[1]/div/div[2]/section[1]/*[position()>1]').xpath(
                'normalize-space(string(.))').extract()),
            2
        )

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))

    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.browser.quit()
