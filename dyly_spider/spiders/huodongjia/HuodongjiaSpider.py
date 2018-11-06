from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

from dyly_spider.spiders.BaseSpider import BaseSpider


class HuodongjiaSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdj"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://www.huodongjia.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['https://www.huodongjia.com/business/']

    def __init__(self, *a, **kw):
        super(HuodongjiaSpider, self).__init__(*a, **kw)
        self.url = "https://www.huodongjia.com/business/"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.driver.get(self.url)
        items = self.driver.find_elements_by_xpath("//html/body/div[2]/div/div[2]/div[4]/ul[1]/li[2]/a")
        for item in items:
            # 获取分类的名称
            name = item.text
            page_Last = 253
            # 设置来源
            source = "活动家"
            if name == "金融财经":
               num =1
               while num < (int(page_Last) + 1):
                   # 设置请求，从第一页循环加载
                   self.driver.get("https://www.huodongjia.com/finance/page-"+str(num)+"/")
                   # 等待3s
                   time.sleep(3)
                   num =num +1
                   params = []
                   # 获取页面数据
                   datas = self.driver.find_elements_by_xpath('//html/body/div[2]/div/div[2]/div[1]/div')
                   for data in datas:
                       try:
                         title = data.find_element_by_xpath('./div/h3/a').text  # 标题
                       except:
                         continue
                       try:
                        times = data.find_element_by_xpath('./div/p[3]/span').text  # 时间
                       except:
                        times = None
                       try:
                        place = data.find_element_by_xpath('./div/p[2]/span').text  # 地点
                       except:
                        place = None
                       try:
                        tags_data = data.find_elements_by_xpath('./div/p/a')  # 标签
                        tag = ""
                        for i, tags in enumerate (tags_data):
                            tag = tag + tags.text
                            if i != len(tags_data) - 1:
                                tag = tag + "、"
                       except:
                        tag = None
                       baseUrl =""
                       try:
                         baseUrl=baseUrl+ data.find_element_by_xpath('./div/a').get_attribute("href")
                       except:
                         baseUrl =None

                       params.append((
                           title,
                           times,
                           place,
                           tag,
                           name,
                           baseUrl,
                           source

                       ))

                   # 插入sql
                   invId = self.insert("""
                                             INSERT INTO `xsbbiz`.`financial_activities` (`title`,`time`,`place`,`tag`, `classify`, `link`, `source`) 
                                             VALUES (%s,%s, %s,%s, %s,%s, %s)
                                             """,
                                       params)






