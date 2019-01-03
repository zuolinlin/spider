import logging
import time
import urllib

from pydispatch import dispatcher
from scrapy import Request, signals
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dyly_spider.items import ZhipinItem
from dyly_spider.spiders.BaseSpider import BaseSpider
from util import cy_logger as logger


# Boss直聘
class ZhiPinSpider(BaseSpider):
    name = "boss_zhipin"
    allowed_domains = ["zhipin.com"]
    company_url = "https://www.zhipin.com/job_detail/?page={}&city=&query={}"

    # 自定义设置
    custom_settings = {
        "LOG_LEVEL": logging.INFO,
        "DOWNLOAD_DELAY": 3,
        'ITEM_PIPELINES': {
            'dyly_spider.pipelines.ZhiPinSpiderPipeline': 100,
        },
    }

    def __init__(self, *a, **kw):
        super(ZhiPinSpider, self).__init__(*a, **kw)
        self.chrome_options = Options()
        #  不打开浏览器窗口
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver',
                                        chrome_options=self.chrome_options)
        self.browser.maximize_window()  # 窗口最大化
        # 隐性等待，最长等3秒
        self.browser.implicitly_wait(3)
        # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
        dispatcher.connect(self.spider_closed, signals.spider_closed)

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
                                  meta={"company": full_name, "current_page": 1, "selenium": True})
                else:
                    yield Request(self.company_url.format(1, name), dont_filter=True,
                                  meta={"company": name, "current_page": 1, "selenium": True})
            current_page += 1

    def parse(self, response):
        company = response.meta['company']
        current_page = response.meta['current_page']
        # 解析数据
        job_list = response.xpath("//div[@class='job-list']/ul/li")
        if len(job_list) > 0:
            for job in job_list:
                item = ZhipinItem()
                item["out_id"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/h3[@class='name']/a/@data-jobid").extract_first()
                item["job_name"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/h3[@class='name']/a/div[@class='job-title']/text()").extract_first()
                item["salary"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/h3[@class='name']/a/span[@class='red']/text()").extract_first()
                item["company_name"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-company']/div[@class='company-text']/h3[@class='name']/a/text()").extract_first()
                item["location"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/p/text()").extract()[0]
                item["years"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/p/text()").extract()[1]
                item["education"] = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/p/text()").extract()[2]
                # item["release_time"] = job.xpath(
                #     "./div[@class='job-primary']/div[@class='info-publis']/p/text()").extract_first()
                item["platform"] = 'BOSS直聘'  # 发布平台
                # 加载详细数据
                detail_url = job.xpath(
                    "./div[@class='job-primary']/div[@class='info-primary']/h3[@class='name']/a/@href").extract_first()
                detail_url = urllib.parse.urljoin(response.url, detail_url)
                time.sleep(3)
                yield Request(detail_url, callback=self.parse_detail, dont_filter=True,
                              meta={"item": item, "selenium": True})
            # 请求下一页
            current_page += 1
            yield Request(self.company_url.format(current_page, company), callback=self.parse, dont_filter=True,
                          meta={"company": company, "current_page": current_page, "selenium": True})

    def parse_detail(self, response):
        item = response.meta['item']
        item["release_time"] = response.xpath(
            "//div[@class='job-banner']/div[@class='inner home-inner']/div[@class='job-primary detail-box']/div[@class='info-primary']/div[@class='job-author']/span[@class='time']/text()") \
            .extract_first()
        print(item)
        yield item

    #   获取公司列表
    def query_company_page(self, page_no=1):
        return self.select_rows_paper(
            sql="SELECT `full_name`,`name` FROM `yx_project`",
            page_no=page_no,
            page_size=20
        )

    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.browser.quit()
