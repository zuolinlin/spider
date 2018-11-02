# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import CookieUtil, date_util


class ProjectSpider(BaseSpider):
    """鲸准创业项目"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 6
    }

    name = "36kr_project"
    allowed_domains = ["36kr.com"]

    list_url = 'https://rong.36kr.com/n/api/column/0/company?sortField=HOT_SCORE&p={page}'
    detail_url = "https://rong.36kr.com/n/api/company/{project_id}"
    members_url = "https://rong.36kr.com/n/api/company/{project_id}/member"
    news_url = "https://rong.36kr.com/n/api/company/{project_id}/news"
    similar_url = "https://rong.36kr.com/n/api/company/{project_id}/similar"

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
        self.cookies = CookieUtil.string_to_dict("acw_tc=276aede715411218167032555e42bb04683ab8263e296f23808e0f5afc6766; kr_stat_uuid=HTXiE25685651; Hm_lvt_e8ec47088ed7458ec32cde3617b23ee3=1541121823,1541139087; download_animation=1; _kr_p_se=d5f0529c-4322-4185-84cc-04bbb54c641e; krid_user_id=1989972187; krid_user_version=2; kr_plus_id=1989972187; kr_plus_token=BQj2Sn1I25rRAMwOjZyifBA26_kuMB2rO824____; _ga=GA1.2.1857322836.1541139094; _gid=GA1.2.1221364596.1541139094; gr_user_id=72208021-04ff-4040-9517-7090ac7f10b4; Hm_lpvt_e8ec47088ed7458ec32cde3617b23ee3=1541139094; kr_plus_utype=0; device-uid=26338060-de66-11e8-a77f-2b77b5dd2aba; krnewsfrontss=5d9cf236babad320756d50fc7426b6ff; M-XSRF-TOKEN=3085ba65843dec7b5c2aa850f12d5b144318c5c457559fbecf0a574c62c9ad35; Z-XSRF-TOKEN=eyJpdiI6InM2ZzZFVE11SWVqSHpcL1VrdkdaNzFBPT0iLCJ2YWx1ZSI6Ino5SjNMUmlEbG45cUJjWTNcL0VId1wvSExJOUtmWWlEZXA0d3ltKzJ5VkhEems4MzNlUTRqN2xSeE9xQTdVZ0NsV3ZYT1JFMFF3N3VuajlFOTNXSkRrdWc9PSIsIm1hYyI6ImViMzYwMzExYjhkZGMzZDExYTAxOWNiOTc3Zjk2NDM1YWRlZGMxNTU3Njc5ODE2NTRlMDM4ODE1NzM2ZDFjODMifQ%3D%3D; krchoasss=eyJpdiI6ImoyV2syTWROWnEyV2ltTDY3QTF3V2c9PSIsInZhbHVlIjoiM2JobGdNcGVcL0lTZVR4SlhBVDdyeCtGZ3l3eFpVTEV2VjNLU0hFaTVpbURJTmFCYnJZczBITnVRcVdiSEpCMHRSU1JTUHQ5ZzE3SDhcL3FQWFVkM2N1Zz09IiwibWFjIjoiNjc0NjFiZTE3NzM5NzViYmY2OGU3OGMzOWVlMTMxMWMyNTRkYzY0MWQwMTc5ZTFhOWNhNmU4M2Y4N2M2ZWJiMyJ9")

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                headers=self.headers,
                cookies=self.cookies,
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
            page = page_data["page"]
            if page == 1:
                total_pages = page_data["totalPages"] + 1
                for url in [self.list_url.format(page=page) for page in range(2, total_pages)]:
                    yield Request(
                        url,
                        headers=self.headers,
                        cookies=self.cookies,
                        dont_filter=True
                    )
            for item in page_data["data"]:
                project_id = item.get("id")
                """项目详情"""
                yield Request(
                    self.detail_url.format(project_id=project_id),
                    headers=self.headers,
                    cookies=self.cookies,
                    dont_filter=True,
                    callback=self.detail
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
