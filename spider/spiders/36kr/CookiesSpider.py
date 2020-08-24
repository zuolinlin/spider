# -*- coding: utf-8 -*-
import os

from scrapy import FormRequest, Request

from spider.spiders.BaseSpider import BaseSpider
from util import CookieUtil


class CookiesSpider(BaseSpider):
    """获取账号登录之前有效Cookies"""

    custom_settings = {
        "COOKIES_ENABLED": True,
        # "COOKIES_DEBUG": True,
        # "AUTOTHROTTLE_ENABLED": True,
        # "DOWNLOAD_DELAY": 6
    }

    name = "36kr_cookies"
    allowed_domains = ["36kr.com"]

    accounts = [
        # {"username": "153671278@qq.com", "password": "95123."},
        # {"username": "18126239571", "password": "95123."},
        {"username": "13530668929", "password": "6802xgcm"},
        {"username": "star23@starmedia.com", "password": "6802xgcm"},
        {"username": "18827388054", "password": "dyly1234"},
        {"username": "18126239581", "password": "dyly123456"},
        {"username": "13556041240", "password": "dyly123456"},
        {"username": "3026130095qq.com", "password": "dyly1234"},
        {"username": "18948715629", "password": "dyly1234"},
        {"username": "18948725656", "password": "dyly332200"},
        {"username": "18124198823", "password": "dyly123456"},
        {"username": "star114@starmedia.com.cn", "password": "q1w2e3r4"},
        {"username": "2059321652@qq.com", "password": "dyly123456"},
        {"username": "2135306534@qq.com", "password": "dyly123456"},
        {"username": "13530668226", "password": "dyly1234"}
    ]

    def __init__(self, *a, **kw):
        super(CookiesSpider, self).__init__(*a, **kw)
        self.headers = {
            "Referer": "https://passport.36kr.com/pages/"
        }
        root = "temp"
        if not os.path.exists(root):
            os.makedirs(root)
        self.file = open(r'temp/36kr_cookies.txt', 'w')

    def start_requests(self):
        form_data = {
            "type": "login",
            "bind": "false",
            "needCaptcha": "false",
            "username": "",
            "password": "",
        }
        for account in self.accounts:
            form_data.update(account)
            yield FormRequest(
                url="https://passport.36kr.com/passport/sign_in",
                headers=self.headers,
                meta={'account': account},
                formdata=form_data,
                callback=self.parse,
                errback=self.error_response
            )  # 还可以通过callback修改回调函数等

    def parse(self, response):
        # acw_tc=276aede715412103811956796e42ad9f633f133234a839650cbd75784821ae; krid_user_version=2
        cookies = response.headers.getlist('Set-Cookie')

        yield Request(
            url="https://rong.36kr.com/api/user/identity",
            cookies=CookieUtil.string_to_dict(
                str(cookies[0], encoding="utf-8").split(";")[0] +
                ";" +
                str(cookies[3], encoding="utf-8").split(";")[0]
            ),
            callback=self.identity,
            dont_filter=True
        )

    def identity(self, response):
        token = response.request.cookies
        cookies = response.headers.getlist('Set-Cookie')
        token.update(
            CookieUtil.string_to_dict(
                str(cookies[0], encoding="utf-8").split(";")[0] +
                ";" +
                str(cookies[1], encoding="utf-8").split(";")[0]
            )
        )
        self.file.write(str(token)+'\n')
        self.file.flush()

    def error_response(self, response):
        self.log_error((
            response.value.response.text,
            response.request.meta["account"]
        ))


if __name__ == '__main__':
    form_data = {
        "type": "login",
        "bind": "false",
        "needCaptcha": "false",
        "username": "",
        "password": "",
    }
    form_data.update({
        "username": "aa",
        "password": "bb",
    })
    print(form_data)


