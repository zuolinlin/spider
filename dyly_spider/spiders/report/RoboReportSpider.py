# -*- coding: utf-8 -*-
import datetime
import json
import time
from scrapy import Request
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import CookieUtil, date_util, QiniuUtil


class RoboReportSpider(BaseSpider):
    # 自定义配置
    custom_settings = {
    }

    name = "robo_report"
    allowed_domains = ["datayes.com"]

    # pub_time_start = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y%m%d")
    pub_time_end = datetime.datetime.now().strftime("%Y%m%d")
    pub_time_start = pub_time_end

    identity = "https://gw.datayes.com/usermaster/identity/nrrp.json"

    start_url = "https://gw.datayes.com/rrp_adventure/web/search?type=EXTERNAL_REPORT&query=&reportType=INDUSTRY" \
                "&pageNow={page_now}&pageSize=20&industry=" \
                "&pubTimeStart={pub_time_start}&pubTimeEnd={pub_time_end}" \
                "&isOptional=false&sortField=&sortOrder=desc&minPageCount=" \
                "&maxPageCount=&isDidMount=true"

    def __init__(self, *a, **kw):
        super(RoboReportSpider, self).__init__(*a, **kw)
        self.cookies = {}

    def start_requests(self):
        yield Request(
            self.identity,
            dont_filter=True
        )

    def parse(self, response):
        cookies = response.headers.getlist('Set-Cookie')
        self.cookies.update(
            CookieUtil.string_to_dict(
                str(cookies[0], encoding="utf-8").split(";")[0] +
                ";" +
                str(cookies[1], encoding="utf-8").split(";")[0]
            )
        )
        yield Request(
            self.start_url.format(page_now=1, pub_time_start=self.pub_time_start, pub_time_end=self.pub_time_end),
            dont_filter=True,
            cookies=self.cookies,
            callback=self.list
        )

    def list(self, response):
        data = json.loads(response.body)
        if data["code"] == 1:
            data = data["data"]
            params = []
            now = time.localtime()
            for item in data["list"]:
                item = item["data"]
                report_id = item.get("id")
                pojo = self.fetchone("SELECT `report_id` FROM `robo_report` WHERE `report_id`=%d AND `source`=0" % report_id)
                if pojo is None:
                    url, size = QiniuUtil.upload(item.get("s3Url", None), "robo-"+str(report_id), "pdf")
                    params.append((
                        report_id,
                        0,
                        item.get("title"),
                        date_util.get_date(item.get("publishTimeStm")),
                        item.get("orgName"),
                        item.get("author"),
                        item.get("ratingContent"),
                        item.get("pageCount"),
                        item.get("industryName"),
                        url,
                        size,
                        now
                    ))
            self.insert("""
                        INSERT INTO `robo_report` (
                          `report_id`,
                          `source`,
                          `title`,
                          `publish_time`,
                          `org_name`,
                          `author`,
                          `rating_content`,
                          `pageCount`,
                          `industry_name`,
                          `pdf`,
                          `size`,
                          `modify_date`
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, params)

            # 分页
            page_now = data["pageNow"]
            if page_now == 1:
                page_count = data["pageCount"]
                while page_now < page_count:
                    page_now = page_now + 1
                    yield Request(
                        self.start_url.format(page_now=page_now, pub_time_start=self.pub_time_start,
                                              pub_time_end=self.pub_time_end),
                        dont_filter=True,
                        cookies=self.cookies,
                        callback=self.list
                    )
        else:
            self.log_error(data)


if __name__ == '__main__':
    print((datetime.datetime.now()+datetime.timedelta(days=-21)).strftime("%Y%m%d"))
    print(datetime.datetime.now().strftime("%Y%m%d"))
