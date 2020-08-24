import json
import logging
import urllib

from scrapy import Request

from spider.items import ZhipinItem
from spider.spiders.BaseSpider import BaseSpider
from util import cy_logger as logger
from util.XPathUtil import str_to_selector


# Boss直聘
class ZhiPinSpider(BaseSpider):
    name = "boss_zhipin"
    allowed_domains = ["zhipin.com"]
    company_url = "https://www.zhipin.com/mobile/jobs.json?page={}&city=&query={}"

    # 自定义设置
    custom_settings = {
        "LOG_LEVEL": logging.WARN,
        "DOWNLOAD_DELAY": 3,
        'ITEM_PIPELINES': {
            'spider.pipelines.ZhiPinSpiderPipeline': 100,
        },
    }

    def __init__(self, *a, **kw):
        super(ZhiPinSpider, self).__init__(*a, **kw)

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
                    yield Request(self.company_url.format(1, full_name), dont_filter=True,
                                  meta={"company": full_name, "current_page": 1})
                else:
                    yield Request(self.company_url.format(1, name), dont_filter=True,
                                  meta={"company": name, "current_page": 1})
            current_page += 1

    def parse(self, response):
        company = response.meta['company']
        current_page = response.meta['current_page']
        result = json.loads(response.body.decode('utf-8'))
        html_str = result['html']
        if len(html_str.strip()) == 0:
            return
        html_str = str_to_selector(html_str)
        if html_str is not None:
            # 解析数据
            job_list = html_str.xpath("//li[@class='item']")
            for job in job_list:
                item = ZhipinItem()
                item["company_name"] = job.xpath("./a//div[@class='name']/text()").extract_first()
                item["job_name"] = job.xpath("./a//div[@class='title']//h4/text()").extract_first()
                item["location"] = job.xpath("./a//div[@class='msg']/em[1]/text()").extract_first()
                item["education"] = job.xpath("./a//div[@class='msg']/em[3]/text()").extract_first()
                item["years"] = job.xpath("./a//div[@class='msg']/em[2]/text()").extract_first()
                item["salary"] = job.xpath("./a//div[@class='title']//span[@class='salary']/text()").extract_first()
                item["platform"] = 'BOSS直聘'  # 发布平台
                item["link"] = job.xpath("./a/@href").extract_first()
                if item["link"] is not None:
                    #   加载详细页
                    item["link"] = urllib.parse.urljoin(response.url, item["link"])
                    yield Request(item["link"], callback=self.parse_detail, meta={"item": item})
            # 请求下一页
            current_page += 1
            yield Request(self.company_url.format(current_page, company), callback=self.parse, dont_filter=True,
                          meta={"company": company, "current_page": current_page})

    def parse_detail(self, response):
        item = response.meta['item']
        item["release_time"] = response.xpath(
            "//div[@class='job-banner']/div[@class='inner home-inner']/div[@class='job-primary detail-box']/div[@class='info-primary']/div[@class='job-author']/span[@class='time']/text()").extract_first()
        yield item

    # 获取公司列表
    def query_company_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `full_name`,`name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )
