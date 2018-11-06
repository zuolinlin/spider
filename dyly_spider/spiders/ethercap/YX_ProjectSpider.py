# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider


class YXProjectSpider(BaseSpider):
    """鲸准创业项目列表"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 2
    }

    name = "ethercap_project"
    allowed_domains = ["ethercap.com"]

    start_url = 'https://source.ethercap.com/api/api/all-up-list?utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7' \
                '&utm_media=web&utm_source=&utm_medium=&utm_activity='

    def __init__(self, *a, **kw):
        super(YXProjectSpider, self).__init__(*a, **kw)
        self.headers = {
            "token": "e1EDKYxT+BzMy2fTmPjZljU4ZjZkMjQ0MzhhY2M3MTc2YTRiNTE5MDNiZWYyZTA0NGU3YjVjNTRlOTY0ZjY0MTVmODdkYWJmNzUwNGEyZTPJ4hByS1MIIti99et2YEBAMplWPI7XLXDZve9DtnCRMSgouwP5SBaUnLIJmmSHWnk=",
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.body = {"page": 0, "limit": 20, "tag": [], "stage": [], "city": [], "country": [], "intersection": 1}

    def start_requests(self):
        yield Request(
            self.start_url,
            headers=self.headers,
            body=json.dumps(self.body),
            method="POST",
            dont_filter=True,
            callback=self.parse,
            errback=self.error_response
        )

    def parse(self, response):
        """
        机构列表
        :param response:
        :return:
        """
        # self.body.update({"page": 100})
        data = self.get_data(response)
        if data is not None:
            params = []
            now = time.localtime()
            for item in data["data"]:
                params.append((
                    item.get("outId"),
                    item.get("projectName"),
                    now
                ))
            self.insert("""
                    INSERT INTO yx_project (
                      `out_id`,
                      `name`,
                      `modify_date`
                    )
                    VALUES (%s, %s, %s)
            """, params)
            # 分页
            if self.body.get("page") == 0:
                count = int(data["count"])
                pages = count / 20 if count % 20 == 0 else int(count / 20) + 1
                # pages = 2
                page = 1
                while page < pages:
                    self.body.update({"page": page})
                    page = page + 1
                    yield Request(
                        self.start_url,
                        headers=self.headers,
                        body=json.dumps(self.body),
                        method="POST",
                        dont_filter=True,
                        callback=self.parse,
                        errback=self.error_response
                    )

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))

    def error_response(self, response):
        self.log_error(response.value.response.text)
