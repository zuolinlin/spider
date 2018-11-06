# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider
from util import date_util


class YXProjectDetailSpider(BaseSpider):
    """鲸准创业项目详情相关"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 2
    }

    name = "ethercap_project_detail"
    allowed_domains = ["ethercap.com"]

    detail_url = "https://source.ethercap.com/api/api/outupdetail?outId={out_id}&uids_verify=94qly7&uids_refer=15&utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7&utm_media=web&utm_source=&utm_medium=&utm_activity="
    basic_info_url = 'https://source.ethercap.com/api/friendup/basicinfo?utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7&utm_media=web&utm_source=&utm_medium=&utm_activity=&outId={out_id}'
    member_url = "https://source.ethercap.com/api/friendup/team?utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7&utm_media=web&utm_source=&utm_medium=&utm_activity=&outId={out_id}"
    news_url = "https://source.ethercap.com/api/friendup/news?utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7&utm_media=web&utm_source=&utm_medium=&utm_activity=&outId={out_id}&limit=6"
    similar_url = "https://source.ethercap.com/api/friendup/competitor?utm_campaign=source&utm_content=jo3mi7gw73ixb94qly7&utm_media=web&utm_source=&utm_medium=&utm_activity=&outId={out_id}&limit=11"

    def __init__(self, *a, **kw):
        super(YXProjectDetailSpider, self).__init__(*a, **kw)
        self.headers = {
            "token": "q5GYLY5NtZNxwSJ1qRpu+jk1MTU3NzZlMjE0ZTM0Y2E4Y2QyYmY3ODgzNzI3NWNkZmE2YTBmYzNhOGI4MzQxYWQ1YzUxZWQ5OGJmZDRlZmVWh5Jn0mUF6ojY+tGjNBiCAPJAfoVlgUPdy8SqU1gC9xM1cPob7GScN8Tu0mPAzeo=",
            "Content-Type": "application/json; charset=UTF-8"
        }

    def start_requests(self):
        # out_id = "aa95a04a8bbef45ccfa3f71498548307"
        current_page = 1
        result = self.query_list_page(current_page)
        pages = result.get("pages")
        # pages = 1
        while current_page <= pages:
            result = self.query_list_page(current_page)
            for row in result.get("rows"):
                out_id = row[0]
                yield Request(
                    self.detail_url.format(out_id=out_id),
                    headers=self.headers,
                    meta={"out_id": out_id},
                    dont_filter=True,
                    callback=self.detail,
                    errback=self.error_response
                )
                yield Request(
                    self.basic_info_url.format(out_id=out_id),
                    headers=self.headers,
                    meta={"out_id": out_id},
                    dont_filter=True,
                    callback=self.basic_info,
                    errback=self.error_response
                )
                yield Request(
                    self.member_url.format(out_id=out_id),
                    headers=self.headers,
                    meta={"out_id": out_id},
                    dont_filter=True,
                    callback=self.member,
                    errback=self.error_response
                )
                yield Request(
                    self.news_url.format(out_id=out_id),
                    headers=self.headers,
                    meta={"out_id": out_id},
                    dont_filter=True,
                    callback=self.news,
                    errback=self.error_response
                )
                yield Request(
                    self.similar_url.format(out_id=out_id),
                    headers=self.headers,
                    meta={"out_id": out_id},
                    dont_filter=True,
                    callback=self.similar,
                    errback=self.error_response
                )
            current_page = current_page + 1
            # time.sleep(40)

    def detail(self, response):
        data = self.get_data(response)
        self.insert("""
                UPDATE 
                  `yx_project` 
                SET
                  `logo` = %s,
                  `name` = %s,
                  `industry` = %s,
                  `website` = %s,
                  `startDate` = %s,
                  `brief` = %s,
                  `intro` = %s,
                  `address1Desc` = %s,
                  `modify_date` = %s 
                WHERE `out_id` = %s
        """, (
            data.get("logoLink", None),
            data.get("projectName", None),
            data.get("upCatgyParentName", None),
            data.get("homepage", None),
            date_util.strptime(data.get("foundDate", None), "%Y-%m"),
            data.get("shortAbstract", None),
            data.get("abstract", None),
            data.get("cityName", None),
            time.localtime(),
            response.meta["out_id"]
        ))

    def basic_info(self, response):
        """
        :param response:
        :return:
        """
        data = self.get_data(response)
        if len(data) > 0:
            self.insert("""
                    UPDATE 
                      `yx_project` 
                    SET
                      `industry_tag` = %s,
                      `full_name` = %s,
                      `modify_date` = %s 
                    WHERE `out_id` = %s
            """, (
                ','.join(data.get("labelArr", [])),
                data.get("companyName", None),
                time.localtime(),
                response.meta["out_id"]
            ))

    def member(self, response):
        """
        :param response:
        :return:
        """
        data = self.get_data(response)
        params = []
        now = time.localtime()
        for item in data:
            if item.get("friendMemberType") == 0:
                params.append((
                    response.meta["out_id"],
                    item.get("name"),
                    item.get("position"),
                    item.get("abstract"),
                    now
                ))
        self.insert("""
                INSERT INTO `yx_project_member` (
                  `out_id`,
                  `name`,
                  `position`,
                  `intro`,
                  `modify_date`
                ) 
                VALUES (%s, %s, %s, %s, %s)
        """, params)

    def news(self, response):
        """
        :param response:
        :return:
        """
        data = self.get_data(response)
        params = []
        now = time.localtime()
        for item in data:
            params.append((
                response.meta["out_id"],
                item.get("title"),
                item.get("source"),
                date_util.strptime(item.get("publishTime", None), "%Y-%m-%d"),
                item.get("link"),
                now
            ))
        self.insert("""
                INSERT INTO `yx_project_news` (
                  `out_id`,
                  `title`,
                  `source`,
                  `publish_date`,
                  `news_url`,
                  `modify_date`
                ) 
                VALUES (%s, %s, %s, %s, %s, %s)
        """, params)

    def similar(self, response):
        """
        :param response:
        :return:
        """
        data = self.get_data(response)
        params = []
        now = time.localtime()
        for item in data:
            params.append((
                response.meta["out_id"],
                item.get("outId"),
                item.get("projectName"),
                item.get("upCatgyParentName"),
                now
            ))
        self.insert("""
                INSERT INTO `yx_project_similar` (
                  `out_id`,
                  `similar_out_id`,
                  `similar_project_name`,
                  `similar_project_similar_info`,
                  `modify_date`
                ) 
                VALUES (%s, %s, %s, %s, %s)
        """, params)

    def error_response(self, response):
        self.log_error(response.value.response.text)

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))

    def query_list_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT out_id, `name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )
