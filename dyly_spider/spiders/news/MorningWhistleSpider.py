# -*- coding: utf-8 -*-
import json
from scrapy import Request
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class MorningWhistleSpider(NewsSpider):
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 3
    }

    name = "morning_whistle"
    allowed_domains = ["morningwhistle.com"]

    start_urls = "http://www.morningwhistle.com/website/content/list?sort=zx&siteId=8&channelFlag=info&isParent=false" \
                 "&lastIndex={}&pageSize={}"
    page = 1
    page_size = 26

    def __init__(self, *a, **kw):
        super(MorningWhistleSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_urls.format(0, self.page_size),
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
            # for row in data.get("rows", []):
            #     row_params = row.get("params", {})
            #     content = XPathUtil.str_to_selector(row_params.get("content"))
            #     self.insert_new(
            #         row.get("id"),
            #         date_util.get_date(row.get("pubDate")),
            #         row.get("title"),
            #         "资讯",
            #         row_params.get("op", "").strip(),
            #         row_params.get("summary"),
            #         "".join(content.xpath('normalize-space(string(.))').extract()),
            #         4
            #     )
            if self.page == 1:
                total = data.get("total")
                page_total = data.get("pageTotal")
                while self.page < page_total:
                    self.page = self.page + 1
                    self.log(self.start_urls.format((self.page-1)*self.page_size-1, self.page_size))
            #     total_count = data.get("total_count")
            #     pages = int(total_count / 20) if total_count % 20 == 0 else int(total_count / 20) + 1
            #     while page < pages:
            #         page = page + 1
            #         yield Request(
            #             self.list_url.format(news_type=response.meta.get("code"), page=page),
            #             meta=response.meta,
            #             dont_filter=True,
            #             callback=self.parse
            #         )

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 1:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))
