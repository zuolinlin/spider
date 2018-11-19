# -*- coding: utf-8 -*-
import json

from scrapy import Request, FormRequest

from dyly_spider.spiders.BaseSpider import BaseSpider


# 公司接口
class ApiCompanySpider(BaseSpider):

    name = 'itjuzi_api_company'

    domain = "http://v1.openapi.itjuzi.com"
    get_token_url = domain + "/oauth2.0/get_access_token"
    company_list_url = domain + "/company/get_company_list?page={page}"
    company_info_url = domain + "/company/get_newly_added_com_info?com_id={com_id}"

    get_token_form = {
        "appid": "123456841",
        "appkey": "Woi41uy65gf75JHds134JHafa209fcMM",
        "granttype": "client_credentials"
    }
    headers = {}
    refresh_token = None
    current_page = 1

    def __init__(self, *args, **kwargs):
        super(ApiCompanySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield FormRequest(
            url=self.get_token_url,
            formdata=self.get_token_form,
            callback=self.parse_page
        )

    def parse_page(self, response):
        data = self.get_data(response)["data"]
        self.headers.update({
            "AUTHORIZATION": "Bearer {access_token}".format(access_token=data.get("access_token"))
        })
        self.refresh_token = data.get("refresh_token")
        yield Request(
            url=self.company_list_url.format(page=self.current_page),
            headers=self.headers,
            dont_filter=True,
            callback=self.company_list
        )

    def company_list(self, response):
        data = self.get_data(response)
        if data is not None:
            # 分页
            if self.current_page == 1:
                # total = data["total"]
                # pages = int(total / 20) if total % 20 == 0 else int(total / 20) + 1
                pages = 2
                while self.current_page < pages:
                    self.current_page = self.current_page + 1
                    yield Request(
                        url=self.company_list_url.format(page=self.current_page),
                        headers=self.headers,
                        dont_filter=True,
                        callback=self.company_list
                    )

            for item in data["data"]:
                yield Request(
                    url=self.company_info_url.format(com_id=item.get("com_id")),
                    headers=self.headers,
                    dont_filter=True,
                    callback=self.company_info
                )

    def company_info(self, response):
        data = self.get_data(response)
        if data is not None:
            data = data["data"]
            data.get("com_id")
            data.get("com_name")
            data.get("com_sec_name")
            data.get("com_registered_name")
            data.get("com_slogan")
            data.get("com_logo")
            data.get("com_logo_archive")
            data.get("com_video")
            data.get("horse_club")
            data.get("com_des")
            data.get("com_url")
            data.get("com_born_year")
            data.get("com_location")
            data.get("com_born_month")
            data.get("com_prov")
            data.get("com_city")
            data.get("com_status_name")
            data.get("com_stage_name")
            data.get("com_fund_needs_name")
            data.get("com_scale_name")
            data.get("com_fund_status_name")
            data.get("com_weibo_url")
            data.get("com_weixin_url")
            data.get("com_cont_tel")
            data.get("com_cont_email")
            data.get("com_cont_addr")
            data.get("cat_id")
            data.get("cat_name")
            data.get("sub_cat_id")
            data.get("sub_cat_name")

    def get_data(self, response):
        data = json.loads(response.body)
        if data["code"] == 1000:
            return data
        else:
            self.log_error("request failed：" + repr(data))
