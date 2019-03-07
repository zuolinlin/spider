import json
from scrapy import Request
import time
from pydispatch import dispatcher
from scrapy import Request, signals
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from dyly_spider.spiders.active.ActiveSpider import ActiveSpider

"""
chinaipo 资本邦==活动会议
"""


class ChinaipoSpider(ActiveSpider):
    name = "chinaipo_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["chinaipo.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://www.chinaipo.com/events/'

    def __init__(self, *a, **kw):
        super(ChinaipoSpider, self).__init__(*a, **kw)
        self.current_page = 1
        # self.chrome_options = Options()
        # #  设置浏览器是否隐藏
        # # self.chrome_options.add_argument('--headless')
        # # self.chrome_options.add_argument('--disable-gpu')
        # # self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        # self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(# executable_path=r'dyly_spider/file/chromedriver.exe',
                                        chrome_options=chrome_options)
        self.driver.get(self.start_urls)
        time.sleep(1)
        ChinaipoSpider.parse(self)
        print("=====已结束=====")

    def parse(self):
            # more_selector = self.driver.find_element_by_xpath('//ul[@class="htnews-ul"]/a')
            # if more_selector.text=="加载更多":
            #     more_selector.click()
            #     time.sleep(1)
            # else:
                data_list = self.driver.find_elements_by_xpath('//ul[@class="htnews-ul"]/li')
                for data in data_list:
                    title = data.find_element_by_xpath('./div/h3/a').text
                    href = data.find_element_by_xpath('./div/h3/a').get_attribute('href')
                    times = data.find_element_by_xpath('./p/span[2]').text
                    times = times[-10:]
                    tags_data = data.find_elements_by_xpath('./div/div[@class="keywdbox-list"]/a')
                    tag = ""
                    for i, tags in enumerate(tags_data):
                        tag = tag + tags.text
                        if i != len(tags_data) - 1:
                            tag = tag + "、"
                    source = '资本邦'
                    classify = "活动会议"
                    self.insert_new(
                         title,
                         times,
                         None,
                         tag,
                         classify,
                         href,
                         source
                    )

                return
