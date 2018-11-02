# -*- coding: utf-8 -*-
import json
import time
from scrapy import Request
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import date_util


class OrgSpider(BaseSpider):
    """鲸准投资机构相关"""

    name = "36kr_org"
    allowed_domains = ["36kr.com"]

    list_url = 'https://rong.36kr.com/n/api/org/list?page={page}'
    detail_url = 'https://rong.36kr.com/n/api/org/{org_id}/basic'
    investment_url = 'https://rong.36kr.com/n/api/org/{org_id}/investment?page={page}'
    member_url = 'https://rong.36kr.com/n/api/org/{org_id}/member'
    member_detail_url = 'https://rong.36kr.com/n/api/investor/{member_id}'
    member_investment_url = 'https://rong.36kr.com/n/api/investor/{member_id}/investment'

    phase_enum = {"UNKNOWN": "未知轮次", "INFORMAL": "战略投资", "NEEQ": "新三板", "NEW_FOUR_BOARD": "新四板", "NONE": "未融资",
                  "SEED": "种子轮", "ANGEL": "天使轮", "PRE_A": "Pre-A轮", "A": "A轮", "A_PLUS": "A+轮", "PRE_B": "Pre-B轮",
                  "B": "B轮", "B_PLUS": "B+轮", "C": "C轮", "C_PLUS": "C+轮", "D": "D轮", "E": "E轮及以后", "PRE_IPO": "Pre-IPO",
                  "ACQUIRED": "并购", "IPO": "上市", "AFTER_IPO": "上市后"}

    """抓取第1页数据"""
    start_urls = [list_url.format(page=1)]

    def __init__(self, *a, **kw):
        super(OrgSpider, self).__init__(*a, **kw)
        self.headers = {
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,
                          headers=self.headers,
                          dont_filter=True)

    def parse(self, response):
        """
        机构列表
        :param response:
        :return:
        """
        data = json.loads(response.body)["data"]["org"]
        page = data["page"]
        if page == 1:
            total_pages = data["totalPages"] + 1
            for url in [self.list_url.format(page=page) for page in range(2, total_pages)]:
                yield Request(url,
                              headers=self.headers,
                              dont_filter=True)
        for item in data["data"]:
            """机构详情"""
            yield Request(
                self.detail_url.format(org_id=item['org']['id']),
                headers=self.headers,
                dont_filter=True,
                callback=self.detail
            )
            """机构投资案例 """
            yield Request(
                self.investment_url.format(org_id=item['org']['id'], page=1),
                headers=self.headers,
                meta={'org_id': item['org']['id']},
                dont_filter=True,
                callback=self.investment
            )
            """成员列表"""
            yield Request(
                self.member_url.format(org_id=item['org']['id']),
                headers=self.headers,
                meta={'org_id': item['org']['id']},
                dont_filter=True,
                callback=self.member
            )

    def detail(self, response):
        """
        机构详情
        :param response:
        :return:
        """
        data = json.loads(response.body)['data']
        if len(data["addresses"]) > 0:
            address = data['addresses'][0]
        else:
            address = {}
        now = time.localtime()
        pojo = self.fetchone("SELECT 1 FROM `jz_org` WHERE org_id = %s" % int(data['id']))
        if pojo is None:
            self.insert("""INSERT INTO `jz_org` (`org_id`,`name_abbr`,`name`,`logo`,`intro`,`enName`,`website`,`startDate`,
                            `city`,`address`,`phone`,`email`,`modify_date`
                            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                data.get('id', ''),
                data.get('nameAbbr', ''),
                data.get('name', ''),
                data.get('logo', ''),
                data.get('intro', ''),
                data.get('enName', ''),
                data.get('website', ''),
                date_util.get_date(data.get('startDate', None)),
                address.get('city', ''),
                address.get('address', ''),
                address.get('phone', ''),
                address.get('email', ''),
                now
            ))
        else:
            self.exec_sql("""
                            UPDATE 
                              `jz_org` 
                            SET
                              `name_abbr` =%s,
                              `name` = %s,
                              `logo` = %s,
                              `intro` = %s,
                              `enName` = %s,
                              `website` = %s,
                              `startDate` = %s,
                              `city` = %s,
                              `address` = %s,
                              `phone` = %s,
                              `email` = %s,
                              `modify_date` = %s 
                            WHERE `org_id` = %s 
            """, (
                data.get('nameAbbr', ''),
                data.get('name', ''),
                data.get('logo', ''),
                data.get('intro', ''),
                data.get('enName', ''),
                data.get('website', ''),
                date_util.get_date(data.get('startDate', None)),
                address.get('city', ''),
                address.get('address', ''),
                address.get('phone', ''),
                address.get('email', ''),
                now,
                data.get('id')
            ))

    def investment(self, response):
        """
        机构投资案例
        :param response:
        :return:
        """
        org_id = response.meta['org_id']
        data = json.loads(response.body)["data"].get("investments", {})
        investments = data.get("data", [])
        params = []
        now = time.localtime()
        for investment in investments:
            project = investment["project"]
            investments = investment["investments"]
            for invest in investments:
                params.append((
                    org_id,
                    project.get("cid", ""),
                    project.get("companyName", ""),
                    invest.get("phaseId", ""),
                    invest.get("phase", ""),
                    invest.get("fundsAmount", ""),
                    date_util.get_date(invest.get('investAt', None)),
                    0,
                    now
                ))
        self.insert("""
                INSERT INTO `jz_investment` (
                              `source_id`,
                              `cid`,
                              `company_name`,
                              `phase_id`,
                              `phase`,
                              `funds_amount`,
                              `invest_at`,
                              `type`,
                              `modify_date`
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, params)
        page = data["page"]
        if page == 1:
            total_pages = data["totalPages"] + 1
            for url in [self.investment_url.format(org_id=org_id, page=page) for page in range(2, total_pages)]:
                yield Request(
                    url,
                    headers=self.headers,
                    meta={'org_id': org_id},
                    dont_filter=True,
                    callback=self.investment
                )

    def member(self, response):
        """
        机构成员列表
        :param response:
        :return:
        """
        members = json.loads(response.body)['data']['member']
        for member in members:
            uid = member['userInfo']['uid']
            yield Request(
                self.member_detail_url.format(member_id=uid),
                headers=self.headers,
                meta={
                    'org_id': response.meta['org_id'],
                    'uid': uid
                },
                dont_filter=True,
                callback=self.member_detail
            )
            yield Request(
                self.member_investment_url.format(member_id=uid),
                headers=self.headers,
                meta={'uid': uid},
                dont_filter=True,
                callback=self.member_investment
            )

    def member_detail(self, response):
        """
        机构成员详情
        :param response:
        :return:
        """
        uid = response.meta['uid']
        org_id = response.meta['org_id']
        data = json.loads(response.body)['data']
        basic = data.get("basic", None)
        if basic is not None:
            now = time.localtime()
            invest_preference = data['investPreference']
            self.insert("""
                        INSERT INTO `jz_member` (
                          `uid`,
                          `org_id`,
                          `org_name`,
                          `avatar`,
                          `name`,
                          `position`,
                          `city`,
                          `focus_industry`,
                          `prefer_phase`,
                          `singleInvest_amount`,
                          `intro`,
                          `modify_date`
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                uid,
                org_id,
                basic.get("orgName", ""),
                basic.get("avatar", ""),
                basic.get("name", ""),
                basic.get("position", ""),
                ','.join(basic.get("city", [])),
                ','.join(invest_preference.get("focusIndustry", [])),
                self.get_prefer_phase(invest_preference.get("preferPhase", [])),
                invest_preference.get("singleInvestAmount"),
                basic.get("intro", ""),
                now
            ))

    def member_investment(self, response):
        """
        机构成员投资案例
        :param response:
        :return:
        """
        uid = response.meta["uid"]
        vo_list = json.loads(response.body)['data'].get("voList", [])
        now = time.localtime()
        params = []
        for vo in vo_list:
            entity_vo = vo["entityVo"]
            for entity in entity_vo:
                params.append((
                    uid,
                    vo.get("cid", ""),
                    vo.get("companyName", ""),
                    None,
                    self.get_phase(entity.get("phase", None)),
                    None,
                    date_util.get_date(entity.get('investDate', None)),
                    1,
                    now
                ))
        self.insert("""
                        INSERT INTO `jz_investment` (
                                      `source_id`,
                                      `cid`,
                                      `company_name`,
                                      `phase_id`,
                                      `phase`,
                                      `funds_amount`,
                                      `invest_at`,
                                      `type`,
                                      `modify_date`
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, params)

    def get_phase(self, key):
        if key is None:
            return None
        return self.phase_enum.get(key, "")

    def get_prefer_phase(self, prefer_phase):
        phases = []
        for phase in prefer_phase:
            phases.append(phase.get("desc"))
        if len(phases) > 0:
            return ','.join(phases),
        else:
            return None


