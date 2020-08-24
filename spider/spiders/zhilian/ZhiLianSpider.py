import logging
import urllib
from scrapy import Request

from spider.items import ZhiLianItem
from spider.spiders.BaseSpider import BaseSpider
from util import cy_logger as logger


# 智联招聘
class ZhiLianSpider(BaseSpider):
    name = "zhi_lian"
    allowed_domains = ["zhaopin.com"]
    company_url = "https://m.zhaopin.com/all-489/?keyword={}&pageindex={}"

    # 自定义设置
    custom_settings = {
        "LOG_LEVEL": logging.WARN,
        # "DOWNLOAD_DELAY": 1,
        'ITEM_PIPELINES': {
            'spider.pipelines.ZhiLianSpiderPipeline': 100,
        },
    }

    def __init__(self, *a, **kw):
        super(ZhiLianSpider, self).__init__(*a, **kw)

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
                    yield Request(self.company_url.format(full_name, 1), dont_filter=True)
                else:
                    yield Request(self.company_url.format(name, 1), dont_filter=True)
            current_page += 1

    def parse(self, response):
        # 解析数据
        job_list = response.xpath("//section[@class='job-list ']")
        for job in job_list:
            item = ZhiLianItem()
            item["link"] = job.xpath("./a/@data-link").extract_first()
            item["company_name"] = job.xpath("./a//div[@class='comp-name fl']/text()").extract_first()
            item["job_name"] = job.xpath("./a//div[@class='job-name fl ']/text()").extract_first()
            item["location"] = job.xpath("./a//span[@class='ads']/text()").extract_first()
            item["salary"] = job.xpath("./a//div[@class='job-sal fr']/div[@class='fl']/text()").extract_first()
            item["release_time"] = job.xpath("./a//div[@class='time fr']/text()").extract_first()
            item["platform"] = '智联招聘'  # 发布平台
            if item["link"] is not None:
                #   加载详细页
                item["link"] = urllib.parse.urljoin(response.url, item["link"])
                yield Request(item["link"], callback=self.parse_detail, meta={"item": item})
        # 加载下一页
        next_page = response.xpath("//div[@class='j_page']//a[@class='nextpage']/@href").extract_first()
        if next_page is not None:
            next_page = urllib.parse.urljoin(response.url, next_page)
            yield Request(next_page, callback=self.parse)

    def parse_detail(self, response):
        item = response.meta['item']
        item["education"] = response.xpath(
            "//div[@class='about-position']/div[@class='job-detail']/div[@class='box1 fl']/span[3]/text()").extract_first().replace(
            "\n", "").strip()
        if len(item["education"]) == 0:
            item["education"] = "学历不限"
        item["years"] = response.xpath(
            "//div[@class='about-position']//span[@class='exp']/text()").extract_first().replace("\n", "").strip()
        if len(item["years"]) == 0:
            item["years"] = "经验不限"
        yield item

    # 获取公司列表
    def query_company_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `full_name`,`name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )
