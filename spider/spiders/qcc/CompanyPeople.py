# -*- coding: utf-8 -*-
import re
import time

from spider.spiders.BaseSpider import BaseSpider
from pydispatch import dispatcher
from scrapy import Request, signals
from selenium import webdriver

from spider.spiders.news.NewsSpider import NewsSpider
from util import XPathUtil


class CompanyPeople(BaseSpider):
    """
    企查查
    """
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'spider.middlewares.SeleniumExtMiddleware': 600
        }
    }

    name = "qichacha"
    allowed_domains = ["qichacha.com"]

    start_url = "https://www.qichacha.com/"

    detail_url = "https://www.qichacha.com"

    start_index = 0

    def __init__(self, *a, **kw):
        super(CompanyPeople, self).__init__(*a, **kw)
        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
                                        chrome_options=chrome_options)
        # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        self.browser.get("https://www.qichacha.com/")
        time.sleep(3)
        #CompanyPeople.parse_list(self)
        CompanyPeople.details(self)
    def parse_list(self):
        pageNo = 500
        while True:
            if pageNo <= 500:
                self.browser.get("https://www.qichacha.com/elib_investfirm.html?p="+str(pageNo))
                time.sleep(1)
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)
                self.browser.execute_script("window.scrollTo(0,0)")
                params = []
                time.sleep(1)
                items = XPathUtil.str_to_selector(self.browser.page_source).xpath("/html/body/div[1]/div[2]/div/div[2]/table/tbody/tr")
                for item in items[self.start_index:]:
                    nav = item.xpath('./th[@class="tx"]/text()').extract_first()
                    if nav !='序号':
                        href =item.xpath('./td[3]/a/@href').extract_first()
                        companyId =str(href).split("id=")[1].split("&")[0]
                        companyNo = item.xpath('./td[1]/text()').extract_first()
                        companyName = item.xpath('./td[3]/a/text()').get().strip()
                        companyFullName = item.xpath('./td[4]/text()').get().strip()
                        detailUrl =self.detail_url + href
                        params.append((
                            companyNo,
                            companyName,
                            companyFullName,
                            detailUrl,
                            companyId
                        ))
                        invId = self.insert("""
                                                                         INSERT ignore INTO `dyly_vc`.`qcc_company` (`companyNo`, `companyName`,`fullName`,`detailUrl`,companyId)
                                                                         VALUES (%s, %s,%s, %s,%s)
                                                                         """,
                                            params)
                pageNo +=1





    def details(self):
        pojo = self.fetchall("SELECT * FROM `dyly_vc`.`qcc_company`  where id >= 26842   ORDER BY companyNo asc    ")
        params = []
        pageNo = 1
        for po in pojo:
            # 机构ID
            detailUrl = po[4]
            id = po[0]
            companyId = po[5]

            self.browser.get(detailUrl)
            time.sleep(1)

            items = XPathUtil.str_to_selector(self.browser.page_source).xpath(
                '//*[@id="Member"]/table/tbody/tr')

            if len(items) ==0:
                continue
            if self.start_index == len(items):
                break

            for item in items[self.start_index:]:
                nav = item.xpath('./th/text()').extract_first()
                if nav != '序号':
                    logoImage = item.xpath('./td[2]/img/@src').extract_first()
                    name = item.xpath('./td[2]/a/text()').extract_first()
                    if  name is None :
                        name = item.xpath('./td[2]/span/text()').extract_first()

                    if name is not None:
                        name = str(name).strip()
                    position = item.xpath('./td[3]/text()').get().strip()
                    des = item.xpath('./td[4]/div/text()').get().strip()
                    params.append((
                        id,
                        name,
                        logoImage,
                        position,
                        des,
                        companyId
                    ))
                    invId = self.insert("""
                                                                     INSERT ignore INTO `dyly_vc`.`qcc_people` (`companyNo`, `name`,`logoimage`,`position`,`des`,companyId)
                                                                     VALUES (%s, %s,%s, %s,%s,%s)
                                                                     """,
                                        params)
                    print("==>>")



    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.browser.quit()

