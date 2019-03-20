# -*- coding: utf-8 -*-
import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from dyly_spider.spiders.news.NewsSpider import NewsSpider

"""
 新浪= 金融新闻
"""


class SinaSpider(NewsSpider):

    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "sina_news"
    allowed_domains = ["sina.com.cn"]
    # 最新
    start_urls = ["http://finance.sina.com.cn/china/"
                  ]

    def __init__(self, *a, **kw):
        super(SinaSpider, self).__init__(*a, **kw)
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
        self.driver.get("http://finance.sina.com.cn/china/")
        time.sleep(1)
        #SinaSpider.new_list(self)
        SinaSpider.detail(self)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def new_list(self):

        JR_click= self.driver.find_element_by_xpath('//div[@class="head-nav wrap js-feed-tab"]/a[@data-feed-urltag="JR"]')
        JR_click.click()
        time.sleep(2)
        while True:
            data_list = self.driver.find_elements_by_xpath('//div[@class="feed-card-content"]/div[7]/div')
            if data_list is not None:
                for data in data_list:
                    detial_url = data.find_element_by_xpath('./h2/a').get_attribute("href")
                    strs = str(detial_url).split("/")
                    out_id = strs[len(strs)-1][0:-6]
                    self.insert_new(
                        out_id,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        detial_url,
                        "37"
                    )
            # 请求下一页

                # next_page = self.driver.find_element_by_xpath('//div[@class="feed-card-page"]/span[@class="pagebox_next"]/a')
                # next_page.click()
                # time.sleep(3)

        # SinaSpider.detail(self)

    def detail(self):
        pojo = self.fetchall(
            "SELECT * FROM `spider_news`  where  spider_source='37' AND content is NULL ORDER BY push_date DESC ")
        if pojo is not None:
            for po in pojo:
                newid = po[0]
                detial_url =po[9]
                self.driver.get(detial_url)
                time.sleep(1)
                try:
                    title = self.driver.find_element_by_class_name("main-title").text
                    push_time = self.driver.find_element_by_class_name("date").text
                    push_time = str(push_time).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                    new_type = "金融财经"
                    source = self.driver.find_element_by_xpath('//div[@class="date-source"]/a').text
                    content = self.driver.find_element_by_class_name("article").get_attribute("outerHTML")
                except:
                   try:
                       title = self.driver.find_element_by_xpath('//div[@class="page-header"]/h1').text
                       push_time = self.driver.find_element_by_class_name("time-source").text
                       push_time = str(push_time).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                       push_time =push_time.split(" ")[0]
                       new_type = "金融财经"
                       source = self.driver.find_element_by_xpath('//span[@class="time-source"]/span/a').text
                       content = self.driver.find_element_by_xpath('//div[@class="article article_16"]').get_attribute("outerHTML")
                   except:
                       pass

                self.exec_sql("""
                                                          UPDATE
                                                            `xsbbiz`.`spider_news`
                                                          SET
                                                            `push_date` =%s,                                          
                                                            `title` =%s,
                                                            `new_type` =%s,
                                                            `source` =%s,
                                                            `content` =%s
                                                          WHERE `spider_source` = 37 and `new_id` =%s
                                                              """, (
                    push_time,
                    title,
                    new_type,
                    "新浪",
                    content,
                    newid

                ))
    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.driver.quit()

