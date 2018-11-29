# -*- coding: utf-8 -*-
import json
from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider
from util import XPathUtil, date_util


class MorningWhistleSpider(NewsSpider):
    """
    晨哨君
    """
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 10,
        "CONCURRENT_REQUESTS": 1
    }

    name = "morning_whistle_news"
    allowed_domains = ["morningwhistle.com"]

    start_url = "http://www.morningwhistle.com/website/content/list?sort=zx&siteId=8&channelFlag=info&isParent=false" \
                "&lastIndex={}&pageSize={}"
    page = 1
    page_size = 26

    def __init__(self, *a, **kw):
        super(MorningWhistleSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_url.format(0, self.page_size),
            dont_filter=True
        )

    def parse(self, response):
        """
        机构列表
        :param response:
        :return:
        """
        data = self.get_data(response)
        if data is not None:
            for row in data.get("rows", []):
                row_params = row.get("params", {})
                content = XPathUtil.str_to_selector(row_params.get("content"))
                out_id = row.get("id")
                self.insert_new(
                    out_id,
                    date_util.get_date(row.get("pubDate")),
                    row.get("title"),
                    "资讯",
                    row_params.get("op", "").strip(),
                    row_params.get("summary"),
                    content,
                    "http://www.morningwhistle.com/info/{out_id}.html".format(out_id=out_id),
                    4
                )
            page_total = data.get("pageTotal")
            if self.page < page_total:
                self.page = self.page + 1
                yield Request(
                    self.start_url.format((self.page - 1) * self.page_size - 1, self.page_size),
                    dont_filter=True,
                    callback=self.parse
                )

    def get_data(self, req):
        body = json.loads(req.body)
        if body["code"] == 1:
            data = body["data"]
            if len(data.get("rows", [])) > 0:
                return data
            else:
                self.log_error("request failed：" + repr(body))
        else:
            self.log_error("request failed：" + repr(body))
