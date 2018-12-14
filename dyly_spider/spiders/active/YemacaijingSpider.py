from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import time
from pydispatch import dispatcher
from scrapy import Request, signals
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

"""
野马财经  == 野马活动、外部活动
"""


class YemacaijingSpider(ActiveSpider):
    name = "yemacaijing_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["yemacaijing.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.yemacaijing.com/Activity'

    base_url = "https://www.yemacaijing.com"

    def __init__(self, *a, **kw):
        super(YemacaijingSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        # self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.browser = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
        #                                 chrome_options=chrome_options)
        self.driver.get(self.start_urls)
        time.sleep(1)
        YemacaijingSpider.detail(self)
        print("=====已结束=====")
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self):
        self.driver.find_element_by_xpath('//*[@id="more"]/a').click()
        time.sleep(2)
        data_list = self.driver.find_elements_by_xpath('//div[@class="layui-col-xs12 layui-col-sm6 layui-col-md4"]')
        for data in data_list:
            title = data.find_element_by_xpath('./div/div/h2/a').text
            href = data.find_element_by_xpath('./div/div/h2/a').get_attribute('href')
            source = '野马财经'
            self.insert_new(
                title,
                None,
                None,
                None,
                None,
                href,
                source
            )

    def detail(self):
        industrys = self.fetchall("SELECT * FROM `xsbbiz`.`financial_activities` where `time` is null ")
        for industry in industrys:
            id = industry[0]
            href = industry[6]
            self.driver.get(href)
            time.sleep(2)
            text = self.driver.find_element_by_xpath('//div[@class="fmt-xinxi"]/dd').text
            times = str(text).split('活动时间：')[1].split(' - ')[0]
            times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
            place = str(text).split('活动地点：')[1].split('活动费用')[0]
            self.exec_sql("""
                          UPDATE 
                            `xsbbiz`.`financial_activities`
                          SEt
                            `time` =%s,
                            `place` =%s
                          WHERE `id` = %s 
                              """, (
                times,
                place,
                id
            ))

    def spider_closed(self):
            self.log("spider closed")
            # 当爬虫退出的时关闭浏览器
            self.browser.quit()
