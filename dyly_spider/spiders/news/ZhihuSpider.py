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

class ZhihuSpider(NewsSpider):
    name = "zhihu_news"
    allowed_domains = ["zhihu.com"]
    # 最新
    start_urls = ["https://zhuanlan.zhihu.com/chuangxin"
                  ]

    def __init__(self, *a, **kw):
        super(ZhihuSpider, self).__init__(*a, **kw)
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
        self.driver.get("https://zhuanlan.zhihu.com/chuangxin")
        time.sleep(1)
        #ZhihuSpider.new_list(self)
        ZhihuSpider.detial(self)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def new_list(self):
        # 定义一个变量用与统计
        self.count = 0
        # 移动到底部 获取下一页数据
        # while 1 == 1:
        #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        #     # 获取列表数据
        #     li_list = self.driver.find_elements_by_xpath('//div[@class="Column-ArticleList"]/div[1]/li[class="ArticleItem"]')
        #     time.sleep(5)
        #     # 获取下拉页有多少条数据
        #     self.cnt = len(li_list)
        #     if self.count == self.cnt:
        #         break
        #     else:
        #         self.count = self.cnt
        li_list = self.driver.find_elements_by_xpath('//section[@class="Column-ArticleList"]/div[1]/li[@class="ArticleItem"]')
        for li in li_list:
            herf = li.find_element_by_xpath('./a[1]').get_attribute("href")
            strs = str(herf).split("/")
            out_id = strs[len(strs)-1]
            self.insert_new(
                out_id,
                None,
                None,
                None,
                None,
                None,
                None,
                herf,
                "39"
            )

        #ZhihuSpider.detial(self)

    def detial(self):

        pojo = self.fetchall(
                "SELECT * FROM `spider_news`  where  spider_source='39' AND content is NULL ORDER BY push_date DESC ")
        if pojo is not None and len(pojo) != 0:
            for po in pojo:
                newid = po[0]
                detial_url = po[9]
                self.driver.get(detial_url)
                title = self.driver.find_element_by_class_name("Post-Title").text
                push_time = self.driver.find_element_by_class_name("ContentItem-time").text
                strs =str(push_time).split(" ")
                push_time = strs[len(strs)-1]
                new_type = "创新工场"
                source = "知乎"
                content = self.driver.find_element_by_xpath('//div[@class="RichText ztext Post-RichText"]').get_attribute("outerHTML")
                time.sleep(2)
                self.exec_sql("""
                                            UPDATE
                                              `xsbbiz`.`spider_news`
                                            SET
                                              `push_date` =%s,                                          
                                              `title` =%s,
                                              `new_type` =%s,
                                              `source` =%s,
                                              `content` =%s
                                            WHERE `spider_source` = 39 and `new_id` =%s
                                                """, (
                    push_time,
                    title,
                    new_type,
                    source,
                    content,
                    newid

                ))

    def spider_closed(self):
            self.log("spider closed")
            # 当爬虫退出的时关闭浏览器
            self.driver.quit()

