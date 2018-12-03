# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider
from util import CookieUtil, date_util


class ProjectDetailSpider(BaseSpider):
    """鲸准创业项目详情"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        # "AUTOTHROTTLE_ENABLED": True,
        # "DOWNLOAD_DELAY": 6
    }

    name = "36kr_project_detail"
    allowed_domains = ["36kr.com"]

    detail_url = "https://rong.36kr.com/n/api/company/{project_id}"
    members_url = "https://rong.36kr.com/n/api/company/{project_id}/member"
    news_url = "https://rong.36kr.com/n/api/company/{project_id}/news"
    similar_url = "https://rong.36kr.com/n/api/company/{project_id}/similar"

    industry_enum = {"E_COMMERCE": "电商", "SOCIAL_NETWORK": "社交", "INTELLIGENT_HARDWARE": "硬件", "MEDIA": "文娱传媒",
                     "SOFTWARE": "工具", "CONSUMER_LIFESTYLE": "消费生活", "FINANCE": "金融", "MEDICAL_HEALTH": "医疗健康",
                     "SERVICE_INDUSTRIES": "企业服务", "TRAVEL_OUTDOORS": "旅游", "PROPERTY_AND_HOME_FURNISHINGS": "房产家居",
                     "EDUCATION_TRAINING": "教育", "AUTO": "汽车交通", "LOGISTICS": "物流", "NON_TMT": "非TMT", "AI": "人工智能",
                     "UAV": "无人机", "ROBOT": "机器人", "VR_AR": "VR·AR", "SPORTS": "体育", "FARMING": "农业", "OTHER": "其他"}

    def __init__(self, *a, **kw):
        super(ProjectDetailSpider, self).__init__(*a, **kw)
        self.headers = {
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                headers=self.headers,
                cookies=self.cookies,
                dont_filter=True
            )

    def detail(self, response):
        data = self.get_data(response)
        if data is not None:
            now = time.localtime()
            project_id = data.get("id", None)
            self.insert("""
                    INSERT INTO `jz_project` (
                      `project_id`,
                      `logo`,
                      `full_name`,
                      `name`,
                      `industry`,
                      `website`,
                      `startDate`,
                      `address1Desc`,
                      `brief`,
                      `industry_tag`,
                      `scale`,
                      `intro`,
                      `modify_date`
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                project_id,
                data.get("logo", None),
                data.get("fullName", None),
                data.get("name", None),
                self.get_industry(data.get("industryEnum", None)),
                data.get("website", None),
                date_util.get_date(data.get("startDate", None)),
                data.get("address1Desc", None),
                data.get("brief", None),
                self.get_industry_tag(data.get("industryTag", None)),
                data.get("scale", None),
                data.get("intro", None),
                now
            ))
            """项目创始团队"""
            yield Request(
                self.members_url.format(project_id=project_id),
                headers=self.headers,
                # cookies=self.cookies,
                meta={'project_id': project_id},
                dont_filter=True,
                callback=self.members
            )
            """项目相关新闻"""
            yield Request(
                self.news_url.format(project_id=project_id),
                headers=self.headers,
                # cookies=self.cookies,
                meta={'project_id': project_id},
                dont_filter=True,
                callback=self.news
            )
            """项目相似项目"""
            yield Request(
                self.similar_url.format(project_id=project_id),
                headers=self.headers,
                # cookies=self.cookies,
                meta={'project_id': project_id},
                dont_filter=True,
                callback=self.similar
            )

    def members(self, response):
        data = self.get_data(response)
        if data is not None:
            project_id = response.meta['project_id']
            now = time.localtime()
            params = []
            members = data.get("members", [])
            for member in members:
                params.append((
                    member.get("id", None),
                    project_id,
                    member.get("name", None),
                    member.get("position", None),
                    member.get("intro", None),
                    now
                ))
            self.insert("""
                    INSERT INTO `jz_project_member` (
                      `member_id`,
                      `project_id`,
                      `name`,
                      `position`,
                      `intro`,
                      `modify_date`
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s)
            """, params)

    def news(self, response):
        data = self.get_data(response)
        if data is not None:
            project_id = response.meta['project_id']
            now = time.localtime()
            params = []
            for new in data:
                params.append((
                    project_id,
                    new.get("title", None),
                    new.get("source", None),
                    date_util.get_date(new.get("publishDate", None)),
                    new.get("newsUrl", None),
                    now
                ))
            self.insert("""
                    INSERT INTO `jz_project_news` (
                      `project_id`,
                      `title`,
                      `source`,
                      `publish_date`,
                      `news_url`,
                      `modify_date`
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s)
            """, params)

    def similar(self, response):
        data = self.get_data(response)
        if data is not None:
            project_id = response.meta['project_id']
            now = time.localtime()
            params = []
            if len(data) > 0:
                company_list = data[0].get("companyList", [])
                for company in company_list:
                    params.append((
                        project_id,
                        company.get("id", None),
                        company.get("name", None),
                        ','.join(company.get("similarInfo", [])),
                        now
                    ))
                self.insert("""
                        INSERT INTO `jz_project_similar` (
                          `project_id`,
                          `similar_project_id`,
                          `similar_project_name`,
                          `similar_project_similar_info`,
                          `modify_date`
                        ) 
                        VALUES (%s, %s, %s, %s, %s)
                """, params)

    def get_industry(self, industry_enum):
        if industry_enum is None:
            return None
        return self.industry_enum.get(industry_enum, None)

    def get_industry_tag(self, industry_tags):
        if industry_tags is None:
            return None
        tags = []
        for tag in industry_tags:
            tags.append(tag.get("name"))
        if len(tags) > 0:
            return ','.join(tags),
        else:
            return None

    def get_data(self, req):
        data = json.loads(req.body)
        if data["code"] == 0:
            return data["data"]
        else:
            self.log_error("request failed：" + repr(data))
