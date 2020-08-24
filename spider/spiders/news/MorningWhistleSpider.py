# -*- coding: utf-8 -*-
import json
from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider
from util import XPathUtil, date_util
import time

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
                timeStamp = row.get("pubDate")
                timeStamp = float(timeStamp / 1000)
                timeArray = time.localtime(timeStamp)
                publishTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                title = row.get("title")
                digest = row_params.get("summary")
                source_url = 'http://www.morningwhistle.com/info/'+str(out_id)+'.html'
                yield Request(
                    source_url,
                    dont_filter=True,
                    meta={"out_id": out_id,
                          "title": title,
                          "publishTime": publishTime,
                          "digest": digest
                          },
                    callback=self.detail
                )


            # page_total = data.get("pageTotal")
            # if self.page < page_total:
            #     self.page = self.page + 1
            #     yield Request(
            #         self.start_url.format((self.page - 1) * self.page_size - 1, self.page_size),
            #         dont_filter=True,
            #         callback=self.parse
            #     )

    def detail(self,response):
        out_id =response.meta['out_id']
        title = response.meta['title']
        publishTime = response.meta['publishTime']
        digest = response.meta['digest']
        content =response.xpath("/html/body").extract_first()

        # print(
        #     out_id,
        #     publishTime,
        #     title,
        #     "资讯",
        #     "晨哨君",
        #     digest,
        #     # content,
        #     response.url,
        #     4
        # )

        self.insert_new(
            out_id,
            publishTime,
            title,
            "资讯",
            "晨哨君",
            digest,
            content,
            response.url,
            4
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
