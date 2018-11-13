from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import datetime
from util import CookieUtil, date_util, QiniuUtil
import re
import uuid
"""
烯牛的研报数据
"""


class XiniuReportSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuNews"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://vip.xiniudata.com"]
    #  开始爬取的地址
    start_urls = ['https://vip.xiniudata.com']

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
    }

    #  设置登陆，
    def __init__(self, *a, **kw):
        super(XiniuReportSpider, self).__init__(*a, **kw)
        self.url = "http://www.xiniudata.com"
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
        self.driver.get(self.url)
        time.sleep(3)  # 睡3毫秒，等待页面加载
        # self.driver.save_screenshot("0.jpg")
        # # 输入账号
        # self.driver.find_element_by_xpath('//*[@id="account"]').send_keys("17621785089")
        # # 输入密码
        # self.driver.find_element_by_xpath('//*[@id="password"]').send_keys("lll123456")
        # # 点击登陆
        # self.driver.find_element_by_xpath(
        #     '//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div/div[3]/div/a').click()
        # time.sleep(10)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())