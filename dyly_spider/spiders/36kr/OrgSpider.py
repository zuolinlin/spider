# -*- coding: utf-8 -*-
import json
import time

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider


# 投资人物
class OrgSpider(BaseSpider):
    # 自定义配置
    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     'dyly_spider.pipelines.ZdbSpiderPipeline': 1,
        # }
    }

    name = "36kr_org"
    allowed_domains = ["36kr.com"]
    list_url = 'https://rong.36kr.com/n/api/org/list?page={page}'
    detail_url = 'https://rong.36kr.com/n/api/org/{id}/basic'
    # 抓取第1页数据
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
        self.log("*" * 100)
        self.log("列表地址===>" + response.url)
        self.log("*" * 100)
        data = json.loads(response.body)["data"]["org"]
        page = data["page"]
        if page == 1:
            total_pages = data["totalPages"]
            self.log(total_pages)
            for url in [self.list_url.format(page=page) for page in range(2, total_pages+1)]:
                yield Request(url,
                              headers=self.headers,
                              dont_filter=True)
        for item in data["data"]:
            yield Request(self.detail_url.format(id=item['org']['id']),
                          headers=self.headers,
                          dont_filter=True,
                          callback=self.detail
                          )

    def detail(self, response):
        self.log("*" * 100)
        self.log("列表地址===>" + response.url)
        self.log("*" * 100)
        data = json.loads(response.body)['data']
        if len(data["addresses"]) > 0:
            address = data['addresses'][0]
        else:
            address = {}
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
                            time.localtime(data.get('startDate', 0)/1000),
                            address.get('city', ''),
                            address.get('address', ''),
                            address.get('phone', ''),
                            address.get('email', ''),
                            time.localtime()
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
                time.localtime(data.get('startDate', 0)/1000),
                address.get('city', ''),
                address.get('address', ''),
                address.get('phone', ''),
                address.get('email', ''),
                time.localtime(),
                data.get('id')
            ))
