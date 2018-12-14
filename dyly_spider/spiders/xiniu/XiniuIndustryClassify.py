from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import datetime
from util import CookieUtil, date_util, QiniuUtil
import re
import uuid
"""
烯牛===全部热点数据
"""


class XiniuIndustryClassify(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuindustryclassify"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["xiniudata.com"]
    #  开始爬取的地址
    start_urls = 'http://www.xiniudata.com/industry/level'
    base_url = 'http://www.xiniudata.com'

    #  设置登陆，
    def __init__(self, *a, **kw):
        super(XiniuIndustryClassify, self).__init__(*a, **kw)

        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
        #                                chrome_options=chrome_options)
        self.driver.get(self.start_urls)
        time.sleep(1)  # 睡3毫秒，等待页面加载
        XiniuIndustryClassify.parse(self)
        print("=======已结束=======")

    def parse(self):
        classifys = self.driver.find_elements_by_xpath('//div[@class="jsx-1682602601 _6nz8G051BDJ5c4wMOs_rX"]/div')
        for classify in classifys:
            classify.click()
            time.sleep(2)
            levelI = classify.text
            datas = self.driver.find_elements_by_xpath('//div[@class="_2r08Jx4IZ_1HgvRiH-JZ7i inner-scroll"]/div[@class="_1kUsB6GPHIoUQzxd7A-wp3"]')
            for data in datas:
                levelII = data.find_element_by_xpath('./div[@class="_2altM-TemIDQ2KuIA613ha"]/a').text
                leverIIIs_selector = data.find_element_by_xpath('./div[@class="OE7fraXfmpqkgMtLM1Hz_"]').text
                if leverIIIs_selector is not None and leverIIIs_selector !='':
                    leverIIIs_selectors = data.find_elements_by_xpath('./div[@class="OE7fraXfmpqkgMtLM1Hz_"]/div')
                    for leverIIIs_selector in leverIIIs_selectors:
                        levelIII = leverIIIs_selector.find_element_by_xpath('./a').text
                        self.insert("""
                                                   INSERT INTO `xsbbiz`.`xiniu_data_industry_classify` (
                                                     `id`,
                                                     `levelI`,
                                                     `levelII`,
                                                     `levelIII`
                                                   ) 
                                                   VALUES (%s,%s,%s,%s)
                                                   """, (
                            str(uuid.uuid4()).replace("-", ""),
                            levelI,
                            levelII,
                            levelIII
                        ))
                else:
                    levelIII =""
                    self.insert("""
                                                                      INSERT INTO `xsbbiz`.`xiniu_data_industry_classify` (
                                                                        `id`,
                                                                        `levelI`,
                                                                        `levelII`,
                                                                        `levelIII`
                                                                      ) 
                                                                      VALUES (%s,%s,%s,%s)
                                                                      """, (
                        str(uuid.uuid4()).replace("-", ""),
                        levelI,
                        levelII,
                        levelIII
                    ))
