
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time


# 陆想汇活动爬取
from dyly_spider.spiders.BaseSpider import BaseSpider


class LjzforumSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "ljz"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://www.ljzforum.com"]
    #  开始爬取的地址
    start_urls = ['https://www.ljzforum.com/activitys.html']

    def __init__(self, *a, **kw):
        super(LjzforumSpider, self).__init__(*a, **kw)
        self.url = "https://www.ljzforum.com/activitys.html"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.driver.get(self.url)

        items = self.driver.find_elements_by_xpath('//html/body/div[8]/div/div[2]/div')
        for item in items:
            # 点击
            item.click()
            #获取分类的名称
            name = item.text
            # 设置来源
            source ="陆想汇"
            if name !="全部":
                while 1 == 1:
                    try:
                        #  点击更多
                        self.driver.find_element_by_xpath('//div[@id="loadMore"]').click()
                        time.sleep(3)
                    except Exception as e:
                        print('Error:', e)
                        break;

                # 插入数据
                params = []

                datas = self.driver.find_elements_by_xpath('//div[@id="data"]/div')

                for data in datas:
                    title = data.find_element_by_xpath('./div[@class="activity_cont"]/div').text  # 标题
                    times = data.find_element_by_xpath('./div[@class="activity_cont"]/div[2]').text  # 时间
                    place = data.find_element_by_xpath('./div[@class="activity_cont"]/div[3]').text  # 地点
                    tag = data.find_element_by_xpath('./div[@class="activity_cont"]/div[5]').text        # 标签
                    numClick = data.get_attribute('onclick')
                    activeNum = numClick[15:-1]
                    # 拼接活动链接
                    baseUrl = "https://www.ljzforum.com/activity/"+activeNum+".html"
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





