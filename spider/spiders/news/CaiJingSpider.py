# -*- coding: utf-8 -*-

import datetime

from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil


class CsSpider(NewsSpider):
    """
    零壹财经
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 6
    # }

    name = "caijing_news"
    allowed_domains = ["01caijing.com"]

    news_type_list = [
        {"code": 1010, "name": "互联网+"},
        {"code": 1016, "name": "消费金融"},
        {"code": 1054, "name": "上市公司"},
        {"code": 1053, "name": "银行科技"},
    ]

    list_url = "https://www.01caijing.com/articles_loading.json?pageIndex={page}&pageSize=20&categoryId={news_type}"

    def __init__(self, *a, **kw):
        super(CsSpider, self).__init__(*a, **kw)

    def start_requests(self):
        page = 1
        for news_type in self.news_type_list:
            news_type.update({"page": page})
            yield Request(
                self.list_url.format(page=page, news_type=news_type.get("code")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        items = response.xpath("//html/body/section")

        # # 下一页
        # page = response.meta.get("page") + 1
        # if len(items) > 0 and page < 2:
        #     # page = response.meta.get("page")+1
        #     response.meta.update({"page": page})
        #     yield Request(
        #         self.list_url.format(page=page, news_type=response.meta.get("code")),
        #         meta=response.meta,
        #         dont_filter=True
        #     )

        for item in items:
            detail_url = "http://" + item.xpath("./dl/dt/a/@href").extract_first()
            out_id =  RegExUtil.find_first(r"/(\d+?).htm", detail_url)
            title = item.xpath("./dl/dt/a/img/@alt").extract_first()
            digest = item.xpath("./dl/dd/p/text()").extract_first()

            push_date = item.xpath("./dl/dd/h3/label/span[@class='icon-time']/text()").extract_first()
            # if push_date.find('年') == -1:
            #     push_date = str(datetime.datetime.now().year) + '年' + push_date

            push_date = push_date.replace(r'年', '-').replace(r'月', '-').replace(r'日', '')

            ti = push_date[-2:]
            if ti == "时前":
                houses = push_date[0:-3]
                push_date = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                    "%Y-%m-%d %H:%M")
            elif ti == "昨天":
                push_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            elif ti == "前天":
                push_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
            elif ti == "天前":
                days = push_date[0:-2]
                push_date = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
            elif ti == "钟前":
                minute = push_date[0:-3]
                push_date = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime("%Y-%m-%d %H:%M")
            elif ti == "周前":
                print(".....")
            elif push_date.count('-') < 2:
                push_date = str(datetime.datetime.now().year) + '-' + push_date
            else:
                push_date = push_date

            response.meta.update({
                "out_id": out_id,
                "push_date": push_date,
                "title" : title,
                # "source": RegExUtil.find_first("(.*) ·", item.xpath("normalize-space(div/div/small/text())")
                #                                .extract_first())
                "digest": digest
            })

            yield Request(
                # "http://" + item.xpath("./dl/dt/a/@href").extract_first()[2:].replace("ejinrong", "article"),
                detail_url,
                meta=response.meta,
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        out_id = response.meta['out_id']
        push_date = response.meta['push_date']
        title = response.meta['title']
        new_type = response.meta['name']
        source = '零壹财经'
        digest = response.meta['digest']
        content = response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 10

        # print(out_id, push_date, title, new_type, source, digest, source_url, spider_source)
        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )
