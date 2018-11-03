# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider
from util import CookieUtil, date_util


class ProjectSpider(BaseSpider):
    """鲸准创业项目列表"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        # "AUTOTHROTTLE_ENABLED": True,
        # "DOWNLOAD_DELAY": 6
    }

    name = "36kr_project"
    allowed_domains = ["36kr.com"]

    list_url = 'https://rong.36kr.com/n/api/column/0/company?sortField=HOT_SCORE&p={page}'

    industry_enum = {"E_COMMERCE": "电商", "SOCIAL_NETWORK": "社交", "INTELLIGENT_HARDWARE": "硬件", "MEDIA": "文娱传媒",
                     "SOFTWARE": "工具", "CONSUMER_LIFESTYLE": "消费生活", "FINANCE": "金融", "MEDICAL_HEALTH": "医疗健康",
                     "SERVICE_INDUSTRIES": "企业服务", "TRAVEL_OUTDOORS": "旅游", "PROPERTY_AND_HOME_FURNISHINGS": "房产家居",
                     "EDUCATION_TRAINING": "教育", "AUTO": "汽车交通", "LOGISTICS": "物流", "NON_TMT": "非TMT", "AI": "人工智能",
                     "UAV": "无人机", "ROBOT": "机器人", "VR_AR": "VR·AR", "SPORTS": "体育", "FARMING": "农业", "OTHER": "其他"}

    """抓取第1页数据"""
    start_urls = [list_url.format(page=1)]

    def __init__(self, *a, **kw):
        super(ProjectSpider, self).__init__(*a, **kw)
        self.headers = {
        }
        self.cookies_list = []
        for line in open(r'temp/36kr_cookies.txt', 'r'):
            self.cookies_list.append(eval(line))

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                headers=self.headers,
                cookies=self.cookies_list[0],
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
            page_data = data["pageData"]
            params = []
            now = time.localtime()
            for item in page_data["data"]:
                params.append((
                    item.get("id"),
                    now
                ))
            self.insert("""
                    INSERT INTO `jz_project` (
                      `project_id`,
                      `modify_date`
                    ) 
                    VALUES (%s, %s)
            """, params)
            page = page_data["page"]
            if page == 1:
                times = 50
                cookies_count = len(self.cookies_list)
                max_pages = cookies_count * times
                total_pages = page_data["totalPages"] + 1
                max_pages = max_pages if total_pages > max_pages else total_pages
                for index, url in enumerate([self.list_url.format(page=page) for page in range(2, max_pages)]):
                    cookies_index = (index + 1) % cookies_count
                    yield Request(
                        url,
                        headers=self.headers,
                        cookies=self.cookies_list[cookies_index],
                        dont_filter=True
                    )

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))


