# -*- coding: utf-8 -*-
import datetime
import json
import time

import requests
from scrapy import Request, FormRequest

from dyly_spider.spiders.BaseSpider import BaseSpider


# 公司接口
class ApiCompanyListSpider(BaseSpider):
    """
    IT桔子公司接口数据抓取
    """

    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOAD_DELAY": 9
    }

    name = 'itjuzi_api_company_list'

    # domain = "http://v1.openapi.itjuzi.com"
    domain = "https://openapi.itjuzi.com"
    get_token_url = domain + "/oauth2.0/get_access_token"
    company_list_url = domain + "/company/get_company_list?page={page}&limit={limit}"

    get_token_form = {
        "appid": "123456841",
        "appkey": "Woi41uy65gf75JHds134JHafa209fcMM",
        "granttype": "client_credentials"
    }
    headers = {}
    refresh_token = None
    current_page = 1
    pages = 0
    limit = 100
    current_date = datetime.datetime.now()

    def __init__(self, current_page=1, *args, **kwargs):
        if current_page is not None and type(current_page) == int:
            self.current_page = current_page
        super(ApiCompanyListSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield FormRequest(
            url=self.get_token_url,
            formdata=self.get_token_form,
        )

    def parse(self, response):
        data = self.get_data(response).get("data", {})
        self.headers.update({
            "AUTHORIZATION": "Bearer {access_token}".format(access_token=data.get("access_token"))
        })
        self.refresh_token = data.get("refresh_token")
        self.log("headers========> " + str(self.headers))
        self.log("refresh_token========> " + self.refresh_token)
        yield Request(
            url=self.company_list_url.format(page=self.current_page, limit=self.limit),
            headers=self.headers,
            dont_filter=True,
            callback=self.company_list
        )

    def company_list(self, response):
        self.exec_refresh_token()
        data = self.get_data(response)
        if data is not None:
            # 分页
            if self.current_page == 1:
                total = data["total"]
                self.pages = int(total / self.limit) if total % self.limit == 0 else int(total / self.limit) + 1
                # pages = 2
                while self.current_page < self.pages:
                    self.current_page = self.current_page + 1
                    yield Request(
                        url=self.company_list_url.format(page=self.current_page, limit=self.limit),
                        headers=self.headers,
                        dont_filter=True,
                        callback=self.company_list
                    )
            for item in data["data"]:
                com_id = item.get("com_id")
                company = self.fetchone("SELECT 1 FROM `itjuzi_company` WHERE com_id=%s" % com_id)
                if company is None:
                    self.insert("""
                            INSERT INTO `itjuzi_company` (
                                              `com_id`,
                                              `com_name`,
                                              `com_sec_name`,
                                              `com_registered_name`,
                                              `com_logo`,
                                              `com_video`,
                                              `horse_club`,
                                              `com_des`,
                                              `com_url`,
                                              `com_born_year`,
                                              `com_born_month`,
                                              `com_prov`,
                                              `com_city`,
                                              `com_location`,
                                              `modify_date`,
                                              `need_sync`
                                            )
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        item.get("com_id"),
                        item.get("com_name"),
                        item.get("com_sec_name"),
                        item.get("com_registered_name"),
                        item.get("com_logo"),
                        item.get("com_video"),
                        item.get("horse_club"),
                        item.get("com_des"),
                        item.get("com_url"),
                        item.get("com_born_year"),
                        item.get("com_born_month"),
                        item.get("com_prov"),
                        item.get("com_city"),
                        item.get("com_location"),
                        time.localtime(),
                        True
                    ))

    def get_data(self, response):
        data = json.loads(response.body)
        if data["code"] == 1000:
            return data
        else:
            self.log_error("request failed：" + repr(data))
            return {}

    def exec_refresh_token(self):
        minute = (datetime.datetime.now() - self.current_date).total_seconds() / 60
        if minute > 50:
            self.get_token_form.update({"granttype": "refresh_token", "refresh_token": self.refresh_token})
            refresh_url = self.get_token_url + "?appid={appid}&appkey={appkey}&granttype={granttype}&refresh_token={" \
                                               "refresh_token}".format(
                appid=self.get_token_form.get("appid"),
                appkey=self.get_token_form.get("appkey"),
                granttype=self.get_token_form.get("granttype"),
                refresh_token=self.get_token_form.get("refresh_token")
            )
            res = requests.get(refresh_url)
            data = json.loads(res.text)
            if data["code"] == 1000:
                self.current_date = datetime.datetime.now()
                self.log("refresh_token_success===>" + repr(data))
            else:
                self.log_error("refresh_token_error===>" + repr(data))

    def set_sql_params(self, params):
        if type(params) == list:
            for i, items in enumerate(params):
                params_list = list(items)
                for j, item in enumerate(params_list):
                    params_list[j] = self.set_sql_value(item)
                    params[i] = tuple(params_list)
        elif type(params) == tuple:
            params_list = list(params)
            for i, item in enumerate(params_list):
                params_list[i] = self.set_sql_value(item)
                params = tuple(params_list)
        return params

    def set_sql_value(self, value):
        if len(str(value)) == 0:
            value = None
        return value
