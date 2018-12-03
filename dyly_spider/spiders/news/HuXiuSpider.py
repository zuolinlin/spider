# -*- coding: utf-8 -*-
import json

from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import RegExUtil, XPathUtil


class HuXiuSpider(NewsSpider):
    """
    虎嗅
    """
    # custom_settings = {
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "DOWNLOAD_DELAY": 9
    # }

    name = "huxiu_news"
    allowed_domains = ["huxiu.com"]

    domain = "https://www.huxiu.com"
    start_url = "https://www.huxiu.com/"
    list_url = "https://www.huxiu.com/v2_action/article_list?page={page}&last_dateline={last_dateline}"

    def __init__(self, *a, **kw):
        super(HuXiuSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_url,
            meta={"page": 1},
            dont_filter=True
        )

    def parse(self, response):
        if self.start_url.__eq__(response.url):
            items = response.xpath("//div[@class='mod-b mod-art clearfix ']")
            last_dateline = response.xpath('//*[@id="index"]/div[2]/div[3]/@data-last_dateline').extract_first()
            for item in items:
                detail_url = item.xpath("div[@class='mob-ctt index-article-list-yh']/h2/a/@href").extract_first()
                if "index_video" not in detail_url:
                    yield Request(
                        self.domain + detail_url,
                        dont_filter=True,
                        meta={
                            "digest": item.xpath("div[@class='mob-ctt index-article-list-yh']/div[2]/text()").extract()[-1].strip()
                        },
                        priority=1,
                        callback=self.detail
                    )
            yield Request(
                self.list_url.format(page=2, last_dateline=last_dateline),
                meta={"page": 2},
                dont_filter=True
            )
        else:
            body = self.get_data(response)
            html = body.get("data")
            if body is not None and len(html) > 0:
                last_dateline = body.get("last_dateline")
                page = response.meta["page"]+1
                response.meta.update({"page": page})
                yield Request(
                    self.list_url.format(page=page, last_dateline=last_dateline),
                    meta=response.meta,
                    dont_filter=True
                )
                html = XPathUtil.str_to_selector(html)
                items = html.xpath("/html/body/div")
                for item in items:
                    detail_url = item.xpath("div[@class='mob-ctt']/h2/a/@href").extract_first()
                    if "index_video" not in detail_url:
                        yield Request(
                            self.domain + detail_url,
                            dont_filter=True,
                            meta={
                                "digest": item.xpath("div[@class='mob-ctt']/div[2]/text()").extract()[-1].strip()
                            },
                            priority=1,
                            callback=self.detail
                        )

    def detail(self, response):
        out_id = RegExUtil.find_first(r"/(\d+?).html", response.url)
        detail = response.xpath('//div[@class="article-wrap"]')
        self.insert_new(
            out_id,
            detail.xpath('normalize-space(div[1]/div/span[1]/text() | div[1]/span[3]/text())').extract_first(),
            detail.xpath('normalize-space(h1/text())').extract_first(),
            "资讯",
            detail.xpath('normalize-space(div[1]/span/a/text())').extract_first(),
            response.meta["digest"],
            response.xpath('//*[@id="article_content'+out_id+'"] | //*[@id="article_content"]'),
            response.url,
            28
        )

    def get_data(self, req):
        body = json.loads(req.body)
        if body["result"] == 1:
            return body
        else:
            self.log_error("request failed：" + repr(body))

