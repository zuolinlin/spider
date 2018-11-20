import json

from scrapy import Request

from dyly_spider.items import BaiduZhaopinItem
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import cy_logger as logger


# 百度招聘
class BaiduZhaopinSpider(BaseSpider):
    name = "baidu_zhaopin"
    allowed_domains = ["baidu.com"]
    referer = "https://zhaopin.baidu.com/m/wise?query=%E8%85%BE%E8%AE%AF"
    company_url = "https://zhaopin.baidu.com/api/wiseasync?pn={}&query={}"

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        'ITEM_PIPELINES': {
            'dyly_spider.pipelines.BaiduZhaopinSpiderPipeline': 100,
        },
    }

    cookies = {
        "BAIDUID": "D69D41C8C6F4145A0B66EF2894F230CF:FG=1",
    }

    headers = {
        "Referer": referer,
        "Connection": "close",
    }

    def __init__(self, *a, **kw):
        super(BaiduZhaopinSpider, self).__init__(*a, **kw)

    def start_requests(self):
        current_page = 1
        result = self.query_company_page(current_page)
        pages = result.get("pages")
        logger.log("公司总页数：" + str(pages))
        while current_page <= pages:
            result = self.query_company_page(current_page)
            for row in result.get("rows"):
                full_name = row[0]
                name = row[1]
                if full_name is not None:
                    yield Request(self.company_url.format(0, full_name), dont_filter=True, cookies=self.cookies,
                                  headers=self.headers, meta={"pn": 0, "company": full_name})
                else:
                    yield Request(self.company_url.format(0, name), dont_filter=True, cookies=self.cookies,
                                  headers=self.headers, meta={"pn": 0, "company": name})
            current_page += 1

    def parse(self, response):
        pn = response.meta['pn']
        company = response.meta['company']
        # 解析数据
        result = json.loads(response.body.decode('utf-8'))
        data = result['data']
        errno = data['errno']
        if errno == 0:
            disp_data = data['disp_data']
            for job in disp_data:
                item = BaiduZhaopinItem()
                item['company_name'] = job['company']
                item['job_name'] = job['name']
                item['location'] = job['city']
                item['education'] = job['education']
                item['years'] = job['experience']
                item['salary'] = job['salary']
                item['release_time'] = job['lastmod']
                item['platform'] = job['provider']
                yield item
            # 加载下一页
            pn += 10
            yield Request(self.company_url.format(pn, company), callback=self.parse, dont_filter=True,
                          meta={"pn": pn, "company": company})

    # 获取公司列表
    def query_company_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `full_name`,`name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )
