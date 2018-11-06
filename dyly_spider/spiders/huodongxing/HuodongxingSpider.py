from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

from dyly_spider.spiders.BaseSpider import BaseSpider


class HuodongxingSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdx"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["http://www.huodongxing.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = ['http://www.huodongxing.com']

    def __init__(self, *a, **kw):
        super(HuodongxingSpider, self).__init__(*a, **kw)
        self.url = "http://www.huodongxing.com/events?isChannel=true&channel=%E8%A1%8C%E4%B8%9A&tag=IT%E4%BA%92%E8%81%94%E7%BD%91"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.driver.get(self.url)
        time.sleep(3)
        # 获取分类点击按钮
        items = self.driver.find_elements_by_xpath('//html/body/section/section[2]/div/ul/li')
        for item in items:

            # 获取分类的名称
            name = item.text
            # 设置来源
            source = "活动行"

            if name !="推荐":
               # 点击
               item.click()
                # 点击全部
               allClick = self.driver.find_element_by_xpath('//*[@id="filterByCity"]/a[1]')
               allClick.click()
               # 等待3s
               time.sleep(3)
               # 获取总页数
               page_Last = self.driver.find_element_by_xpath('//a[@class="layui-laypage-last"]').text
               num = 1
               while num < (int(page_Last) + 1):
                   # 设置请求，从第一页循环加载
                   self.driver.get("http://www.huodongxing.com/events?orderby=o&channel=行业&tag="+name
                                   +"&city=全部&isChannel=true&page="+str(num))
                   # 等待3s
                   time.sleep(3)
                   num =num +1
                   params = []
                   # 获取页面数据
                   datas = self.driver.find_elements_by_xpath('//html/body/section/section[5]/section/div[2]/div[2]/div')
                   for data in datas:
                       try:
                        # 判断是否为精选或者最新，如果是精选或者最新直接跳过
                        data.find_element_by_xpath('./a/div/div/img')  # 标题
                        continue
                       except:
                        title = data.find_element_by_xpath('./a/div/div').text  # 标题
                       try:
                        times = "2018年"+data.find_element_by_xpath('./a/div/p').text  # 时间
                       except:
                        times = None
                       try:
                        place = data.find_element_by_xpath('./a/div/div[2]').text  # 地点
                       except:
                        place = None
                       try:
                        tags_data = data.find_elements_by_xpath('./a/div[2]/div/div/p')  # 标签
                        tag = ""
                        for i, tags in enumerate (tags_data):
                            tag = tag + tags.find_element_by_xpath("./span").text
                            if i != len(tags_data) - 1:
                                tag = tag + "、"
                       except:
                        tag = None
                       baseUrl =""
                       try:
                         baseUrl=baseUrl+ data.find_element_by_xpath('./a').get_attribute("href")
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






