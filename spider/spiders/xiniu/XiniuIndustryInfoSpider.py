from spider.spiders.BaseSpider import BaseSpider
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


class XiniuIndustryInfoSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuindustryinfo"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["xiniudata.com"]
    #  开始爬取的地址
    start_urls = 'http://www.xiniudata.com/industry/hot'
    base_url = 'http://www.xiniudata.com'

    #  设置登陆，
    def __init__(self, *a, **kw):
        super(XiniuIndustryInfoSpider, self).__init__(*a, **kw)

        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
        #                                chrome_options=chrome_options)
        self.driver.get(self.start_urls)
        time.sleep(1)  # 睡3毫秒，等待页面加载
        XiniuIndustryInfoSpider.detail(self)
        print("=======已结束=======")

    def parse(self):
        classifys = self.driver.find_elements_by_xpath('//div[@class="km2piz_FdnLXBJlL76pOq"]/div')
        for classify in classifys:
            classifyName = classify.find_element_by_xpath('./div[@class="_3bvTmrCyBKiXM4p6QmxuHu"]/span').text  # 分类名称
            industrys = classify.find_elements_by_xpath('./div[@class="_3f7-CbjRt_KlnjUaBl375W "]/div')
            for industry in industrys:
                linkUrl = industry.find_element_by_xpath('./a').get_attribute('href')
                industryName = industry.text
                industryName = str(industryName).split(' (')[0]
                outId = linkUrl[34:-9]

                self.insert("""
                                           INSERT INTO `xsbbiz`.`xiniu_data_industry_info` (
                                             `id`,
                                             `outId`,
                                             `classifyName`,
                                             `industryName`,
                                             `linkUrl`
                                           ) 
                                           VALUES (%s,%s,%s,%s, %s)
                                           """, (
                    str(uuid.uuid4()).replace("-", ""),
                    outId,
                    classifyName,
                    industryName,
                    linkUrl
                ))
        print("=================")

    def detail(self):
        industrys = self.fetchall("SELECT * FROM `xsbbiz`.`xiniu_data_industry_info` where description is null ")
        for industry in industrys:
            id = industry[0]
            linkUrl = industry[5]
            self.driver.get(linkUrl)
            description = self.driver.find_element_by_xpath('//div[@class="jsx-3002069646 _17KX9AFbtNnLJN2xjsNEJe dIl-iYgYvAWx85U8Uw1YT"]/pre').text
            self.exec_sql("""
                                          UPDATE 
                                            `xsbbiz`.`xiniu_data_industry_info`
                                          SEt
                                            `description` =%s
                                          WHERE `id` = %s 
                                              """, (
                description,
                id
            ))
