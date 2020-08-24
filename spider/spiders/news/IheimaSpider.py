# -*- coding: utf-8 -*-
import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
import uuid
from util.XPathUtil import str_to_selector
from scrapy import Request, signals
from pydispatch import dispatcher
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import datetime
import re
from spider.spiders.news.NewsSpider import NewsSpider

"""
I黑马  产业  资本动态
"""


class IheimaSpider(NewsSpider):

    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "iheima_news"
    allowed_domains = ["iheima.com"]
    # 金融与科技
    start_urls = ["http://www.iheima.com/scope/1"
                  ]

    def __init__(self, *a, **kw):
            super(IheimaSpider, self).__init__(*a, **kw)
            self.current_page = 1
            self.chrome_options = Options()
            #  设置浏览器是否隐藏
            # self.chrome_options.add_argument('--headless')
            # self.chrome_options.add_argument('--disable-gpu')
            # self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
            self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
            #

            # chrome_options = webdriver.ChromeOptions()
            # # 不打开浏览器窗口
            # chrome_options.add_argument('headless')
            # chrome_options.add_argument('no-sandbox')
            # self.driver = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
            #                                 chrome_options=chrome_options)
            # 产业
            # self.driver.get("http://www.iheima.com/scope/1")
            # 资本动态
            self.driver.get("http://www.iheima.com/scope/89")
            time.sleep(1)
            #IheimaSpider.news_list(self)

            IheimaSpider.detail(self)
           #  dispatcher.connect(self.spider_closed, signals.spider_closed)

    def news_list(self):

        while True:
            try:
                lodemore = self.driver.find_element_by_class_name('lodemore')
                lodemore.click()
                time.sleep(2)
            except:
              data_list = self.driver.find_elements_by_xpath('//div[@class="item-wrap clearfix"]')
              for data in data_list:
                sourceUrl = data.find_element_by_xpath('./a[@class="pic distable-cell"]').get_attribute("href")
                strs = str(sourceUrl).split("/")
                out_id = strs[len(strs)-1][0:-5]
                push_data = data.find_element_by_class_name("time").text
                self.insert_new(
                    out_id,
                    push_data,
                    None,
                    "资本动态",
                    None,
                    None,
                    None,
                    sourceUrl,
                    "15"
                )

    def detail(self):
        pojo = self.fetchall(
            "SELECT * FROM `spider_news`  where  spider_source='15' AND content is NULL ORDER BY push_date DESC ")
        if pojo is not None:
            for po in pojo:
                new_id = po[0]
                detial_url = po[9]
                self.driver.get(detial_url)
                time.sleep(3)
                try:
                   title = self.driver.find_element_by_xpath('//div[@class="main-content"]/div[@class="title"]').text
                   source = "i黑马"
                   digest = self.driver.find_element_by_xpath('//div[@class="outline"]/p').text
                   contents = self.driver.find_elements_by_xpath('//div[@class="main-content"]/p')
                   content = ""
                   for c in contents:
                      html = c.get_attribute("outerHTML")
                      content += str(html)
                   self.exec_sql("""
                                                             UPDATE
                                                               `xsbbiz`.`spider_news`
                                                             SET
                                                               `digest` =%s,                                          
                                                               `title` =%s,                                     
                                                               `source` =%s,
                                                               `content` =%s
                                                             WHERE `spider_source` = 15 and `new_id` =%s
                                                                 """, (
                           digest,
                           title,
                           source,
                           content,
                           new_id

                   ))
                except:
                    pass




