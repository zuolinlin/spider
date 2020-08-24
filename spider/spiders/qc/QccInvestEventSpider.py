import uuid

from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time


class QccInvestEventSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "qccInvestEventSpider"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://www.qichacha.com/"]
    #  开始爬取的地址
    start_urls = ['https://www.qichacha.com/']
    list_url = "https://www.qichacha.com/elib_financing.shtml?province={province}&round=&industry=&date=&p={page}"
    #
    province_type_list = [
        {"code": "XZ", "name": "西藏自治区"},
        {"code": "SAX", "name": "陕西省"},
        {"code": "GS", "name": "甘肃省"},
        {"code": "QH", "name": "青海省"},
        {"code": "NX", "name": "宁夏回族自治区"},
        {"code": "XJ", "name": "新疆维吾尔自治区"},
        {"code": "TW", "name": "台湾省"},
        {"code": "HK", "name": "香港特别行政区"},
        {"code": "MO", "name": "澳门特别行政区"},
    ]

    def __init__(self, *a, **kw):
        super(QccInvestEventSpider, self).__init__(*a, **kw)
        # # self.url = "https://vip.xiniudata.com"
        # self.url = "https://www.qichacha.com/"
        # self.chrome_options = Options()
        # #  设置浏览器是否隐藏
        # # self.chrome_options.add_argument('--headless')
        # # self.chrome_options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        #
        # # chrome_options = webdriver.ChromeOptions()
        # # # 不打开浏览器窗口
        # # chrome_options.add_argument('headless')
        # # chrome_options.add_argument('no-sandbox')
        # # self.driver = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
        # #                                chrome_options=chrome_options)
        # self.driver.get("https://www.qichacha.com/elib_financing")
        # time.sleep(1)  # 睡3毫秒，等待页面加载
        #
        #
        # onclick = self.driver.find_element_by_xpath('//div[@class="pills province"]/div[@class="pills-after"]/a[27]')
        # onclick.click()
        # for i in range(2, 46):
        #     industryOnclick = self.driver.find_element_by_xpath('//div[@class="pills industry"]/div[@class="pills-after"]/a['+str(i)+"]")
        #     industryOnclick.click()
        #     datas = self.driver.find_elements_by_xpath('//table[@class="ntable"]/tbody/tr')
        #     if datas is not None and datas.__len__() != 0:
        #         params = []
        #         for data in datas:
        #            # logo = data.find_element_by_xpath('./td[1]/img').get_attribute("src")
        #             name = data.find_element_by_xpath('./td[2]').text
        #             fullName = data.find_element_by_xpath('./td[3]').text
        #             company = data.find_element_by_xpath('./td[4]').text
        #             roundName = data.find_element_by_xpath('./td[5]').text
        #             roundMoney = data.find_element_by_xpath('./td[6]').text
        #             invDate = data.find_element_by_xpath('./td[7]').text
        #             params.append((
        #                 str(uuid.uuid4()).replace("-", ""),
        #                 name,
        #                 fullName,
        #                 roundName,
        #                 roundMoney,
        #                 invDate,
        #                 company,
        #                 1,
        #                 "XZ",
        #                 logo
        #             ))
        #         self.insert("""
        #                      INSERT INTO `dyly_vc`.`invest_event_qc` (`inv_event_id`, `name`,`full_name`,`round_name`, `round_money`,`inv_date`,inv_companyNames,industry_code,province_code,logo)
        #                      VALUES (%s, %s,%s,%s, %s,%s, %s, %s, %s,%s)
        #                      """,
        #                     params)
        #         print(datas)
        #         # 获取下一页的数据
        #         nextClick = self.driver.find_element_by_xpath('//nav[@class="text-right"]/ul/li[last()]')
        #         nextClick.click()

    def start_requests(self):
        # proxies = {'http': 'http://183.148.131.6:9999', 'https': 'https://182.111.120.11:9999'}
        for province in self.province_type_list:
            yield Request(
                self.list_url.format(province=province.get("code"), page=1),

                meta=province
            )


    def parse(self, response):
        tbody = response.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/table//tr')
        if len(tbody) !=0:
            for tr in tbody:
                logo = tr.xpath('./td[1]/src').extract_first()
                projectName = tr.xpath('./td[2]/text()').extract_first()
                fullName = tr.xpath('./td[3]/text()').extract_first()
                logo = tr.xpath('./td[4]/text()').extract_first()
                comoany = tr.xpath('./td[5]/text()').extract_first()
                roundName = tr.xpath('./td[6]/text()').extract_first()
                invDate = tr.xpath('./td[7]/text()').extract_first()

        print(tbody)