from dyly_spider.items import XiniuInstitutionItem, XiniuInvestmentEvents, XiniuInstitudynamic, XiniuNews, XiniuFun, \
    XiniuFundmanager, XiniuLP
from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import os
import uuid

# 投资人物
# 烯牛的机构数据Spider类 继承BaseSpider


class IpoSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "ipo"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://ipo.sac.net.cn"]
    #  开始爬取的地址
    start_urls =['https://ipo.sac.net.cn/pages/inquiryObject/xjdxml.html']

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
    }
    # 定义一个变量用与统计
    count = 0
    #  设置登陆，
    def __init__(self, *a, **kw):
        super(IpoSpider, self).__init__(*a, **kw)
        # self.url = "https://vip.xiniudata.com"
        self.url = "https://ipo.sac.net.cn/pages/inquiryObject/xjdxml.html"
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
        # self.driver.find_element_by_xpath('//*[@id="account"]').send_keys("18565679500")
        # # 输入密码
        # self.driver.find_element_by_xpath('//*[@id="password"]').send_keys("wzy123")
        # # 点击登陆
        # self.driver.find_element_by_xpath(
        #     '//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div/div[3]/div/a').click()
        # time.sleep(10)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())
        self.driver.get("https://ipo.sac.net.cn/pages/inquiryObject/xjdxml.html")
        # self.driver.get("https://vip.xiniudata.com/org/investor/")
        time.sleep(2)
        #XiniuSpider.get_xinniu_investment_events(self)
        IpoSpider.get_list_data(self)
    # 获取烯牛机构的列表页数据
    def get_list_data(self):
        self.count = self.count + 1
        # 移动到底部 获取下一页数据  701
        for i in range(0, 560):
        # while count <= 6:

            # 获取列表数据
            li_list = self.driver.find_elements_by_xpath('//tbody/tr[@class="ui-widget-content jqgrow ui-row-ltr"]')
            time.sleep(2)

            params = []
            # 遍历读取写入数据库
            for li in li_list:
                iOI_NAME = li.find_element_by_xpath("./td[3]").text
                iOCI_LINKMAN_EMAIL = li.find_element_by_xpath("./td[4]").text
                params.append((
                    "推荐类个人投资者",
                    iOI_NAME,
                    iOCI_LINKMAN_EMAIL
                ))
            # 插入sql
            invId = self.insert("""
                                                     INSERT INTO `xsbbiz`.`ipo_sac` (`RNUM`, `IOI_NAME`,`IOCI_LINKMAN_EMAIL`)
                                                     VALUES (%s, %s,%s)
                                                     """,
                                params)

            next_butten = self.driver.find_element_by_xpath('//td[@id="next"]')
            next_butten.click()
            time.sleep(5)
            print("===")

