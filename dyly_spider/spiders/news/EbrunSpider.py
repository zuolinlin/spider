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
异邦新闻
"""


class EbrunSpider(NewsSpider):
    # custom_settings = {
    #     "COOKIES_ENABLED": True,
    # }

    name = "ebrun_new"
    allowed_domains = ["ebrun.com"]
    # 最新
    start_urls = ["http://www.ebrun.com/top/1"
                  ]

    def __init__(self, *a, **kw):
        super(EbrunSpider, self).__init__(*a, **kw)
        self.current_page = 1
        # self.chrome_options = Options()
        # #  设置浏览器是否隐藏
        # # self.chrome_options.add_argument('--headless')
        # # self.chrome_options.add_argument('--disable-gpu')
        # self.browser = webdriver.Chrome(chrome_options=self.chrome_options)

        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
        #                                chrome_options=chrome_options)
        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
                                        chrome_options=chrome_options)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        url = "http://www.ebrun.com/top/1"
        yield Request(
                url=url,
                meta={"selenium": True}
            )

    def parse(self, response):
        data_list = str_to_selector(self.browser.page_source).xpath('//div[@class="sublevel-panel"]//div[@data-type="article"]')
        if data_list is not None and len(data_list):
            # params = []
            for data in data_list:
                title = data.xpath('./a/div[@class="liebiao-well"]/p[@class="liebiao-xinwen-title"]/text()').extract_first()  # 标题
                url = data.xpath('./a[@acpos="www.ebrun.com_chan_lcol_fylb"]/@href').extract_first()  # url
                out_id = data.xpath('@data-id').extract_first()
                push_time = data.xpath('./div[@class="liebiao-xinwen-side"]/p[@class="time"]/text()').extract_first()  # 时间
                digest = data.xpath('./a/div[@class="liebiao-well"]/p[@class="liebiao-xinwen-des"]/text()').extract_first()  # 摘要
                new_type = "top"
                spider_source = 13
                self.insert_new(
                    out_id,
                    push_time,
                    title,
                    new_type,
                    url,
                    digest,
                    None,
                    spider_source
                )

                # params.append((
                #     new_id,
                #     out_id,
                #     push_time,
                #     title,
                #     new_type,
                #     url,
                #     digest,
                #     None,
                #     spider_source,
                #     time.localtime()
                # ))
            # 插入sql
            # invId = self.insert("""
            #                        INSERT INTO `spider_news` (
            #                           `new_id`,
            #                           `out_id`,
            #                           `push_date`,
            #                           `title`,
            #                           `new_type`,
            #                           `source`,
            #                           `digest`,
            #                           `content`,
            #                           `spider_source`,
            #                           `modify_date`
            #                         )
            #                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            #                        """,
            #                     params)



            time.sleep(3)
            # 获取下一页的数据
            pages = 6655
            while self.current_page < pages:
                self.current_page += 1
                next_url = "http://www.ebrun.com/top/" + str(self.current_page)
                yield Request(next_url, meta={"selenium": True}, callback=self.parse)

    def detail(self, response):
        source = response.xpath('normalize-space(//article/div/p[@class="source"]/span[2]/text())').extract_first()  # 来源
        source = str(source).split(": ")[1]
        content = response.xpath('normalize-space(//div[@class="post-text"])').getall()
        content = "".join(content).strip()
        self.insert_new(
            source,
            content
        )

    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.browser.quit()

