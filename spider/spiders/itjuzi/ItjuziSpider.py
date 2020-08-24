# -*- coding: utf-8 -*-
import json

import jsonpath
from scrapy import FormRequest, Request
from util import cy_logger as logger

from spider.items import ItjuziCompanyItem
from spider.spiders.BaseSpider import BaseSpider


# 公司
class ItjuziSpider(BaseSpider):
    name = 'itjuzi'
    allowed_domains = ['itjuzi.com']

    list_url = 'http://radar.itjuzi.com/company/infonew?page={}'
    start_urls = [list_url.format(1)]

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2.2,
        'ITEM_PIPELINES': {
            'spider.pipelines.ItjuziSpiderPipeline': 2,
        },
    }

    cookies = {
        "_ga": "GA1.2.1756283862.1540457967",
        "gr_user_id": "5dbc8ed8-73e6-432a-a473-2df646ab1938",
        "acw_tc": "781bad0715404580051513986e436ddaa77ca283e228a0596ec3dde3ad4f2f",
        "identity": "13530668226%40test.com",
        "remember_code": "513J3uLO1v",
        "unique_token": "660922",
        "Hm_lvt_80ec13defd46fe15d2c2dcf90450d14b": "1540524296",
        "MEIQIA_EXTRA_TRACK_ID": "1C3pCKam0l3XgJBOQ7mkhXKcpQM",
        "_gid": "GA1.2.1877352760.1540775392",
        "Hm_lvt_1c587ad486cdb6b962e94fc2002edf89": "1540457968,1540775392",
        "MEIQIA_VISIT_ID": "1CECUkyW22fyYMrThNHQGZxANBj",
        "Hm_lpvt_80ec13defd46fe15d2c2dcf90450d14b": "1540778079",
        "user-radar.itjuzi.com": "%7B%22n%22%3A%22%5Cu6854%5Cu53cbd1f58ac3feb0c%22%2C%22v%22%3A2%7D",
        "Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89": "1540796918",
        "gr_session_id_eee5a46c52000d401f969f4535bdaa78": "62fa4b7e-8bc4-4fb6-9270-6136652febaf",
        "gr_cs1_62fa4b7e-8bc4-4fb6-9270-6136652febaf": "user_id%3A660922",
        "gr_session_id_eee5a46c52000d401f969f4535bdaa78_62fa4b7e-8bc4-4fb6-9270-6136652febaf": "true",
        "session": "63089699ff48305f7dddbbde9be25ea274b0093e"
    }

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, *args, **kwargs):
        super(ItjuziSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, cookies=self.cookies, callback=self.parse_page, headers=self.headers, dont_filter=True)

    def parse_page(self, response):
        # 把json数据转换成Python对象
        company_list = json.loads(response.body.decode('utf-8'))
        logger.log("列表地址===>" + response.url)
        # 总共有多少页：
        page_count = jsonpath.jsonpath(company_list, '$..data')[0]['page_total']
        logger.log(page_count)

        # 当前第几页：
        now_page = jsonpath.jsonpath(company_list, '$..data')[0]['page_num']
        logger.log(now_page)

        if now_page == 1:
            for url in [self.list_url.format(page) for page in range(2, page_count + 1)]:
                yield Request(url, cookies=self.cookies, callback=self.parse_page, headers=self.headers,
                              dont_filter=True)

        companys = jsonpath.jsonpath(company_list, '$..data')[0]['rows']

        for company in companys:
            item = ItjuziCompanyItem()

            # 解析想要的字段：
            item["company_name"] = company["com_name"]
            # logo地址
            item["company_logo"] = company['com_logo_archive']

            # 公司id
            item['company_id'] = company['com_id']
            # 公司描述
            item["company_des"] = company['com_des']
            # 公司行业
            item["company_fa"] = company['com_cat_name']
            # 公司子行业
            item["company_son"] = company['com_sub_cat_name']

            # 最新融资情况由四步分组成：
            invse_date = company['invse_date']
            invse_round_id = company['invse_round_id']
            invse_detail_money = company['invse_detail_money']
            invse_total_money = company['invse_total_money']

            # 公司最新融资情况
            item[
                "company_recent"] = invse_date + ' ' + invse_round_id + ' ' + invse_detail_money + ' ' + invse_total_money
            # 公司资产总额
            item["company_count"] = company['invse_total_money']
            # 公司估价
            item["company_money"] = company['guzhi']

            # 公司地址
            item['company_addr'] = company['com_addr']
            # 公司标语
            item['company_slogan'] = company['com_slogan']

            # 公司成立时间
            item["company_btime"] = company['com_born_date']
            # 公司规模
            item["company_people"] = company['com_scale']
            # 公司营运情况
            item["company_operate"] = company['com_status']

            # 发送详细页的请求
            yield FormRequest("https://www.itjuzi.com/company/" + item['company_id'], cookies=self.cookies,
                              meta={'meta1': item}, callback=self.parse_detail, headers=self.headers, dont_filter=True)

    # 解析详细页
    def parse_detail(self, response):
        item = response.meta["meta1"]
        # 详细页里面的
        # 公司全名
        item["company_fullname"] = response.xpath('//div[@class="des-more"]/h2/text()').extract()[0]
        # 团队人员姓名
        item["perosonname"] = response.xpath('//div[@class="sec"]//a[@class="person-name"]/text()').extract()[0]
        # 职位
        item["perosonposition"] = response.xpath('//div[@class="sec"]//div[@class="per-position"]/text()').extract()[0]
        # 个人简介
        item["perosondes"] = response.xpath('//div[@class="sec"]//div[@class="per-des"]/div/text()').extract()[
            0].strip()
        # 公司产品
        item["product"] = response.xpath(
            '//div[@class="sec panel-for-scroll"]//div[@class="product-list empty-list empty-with-link"]/div/text()').extract()[
            0]
        yield item
