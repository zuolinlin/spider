from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import os

# 投资人物
# 烯牛的机构数据Spider类 继承BaseSpider


class XiniuSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniu"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://vip.xiniudata.com"]
    #  开始爬取的地址
    start_urls =['https://vip.xiniudata.com']

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
    }

    #  设置登陆，
    def __init__(self, *a, **kw):
        super(XiniuSpider, self).__init__(*a, **kw)
        self.url = "https://vip.xiniudata.com"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        #  self.chrome_options.add_argument('--headless')
        #  self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.driver.get(self.url)
        time.sleep(3)  # 睡3毫秒，等待页面加载
        self.driver.save_screenshot("0.jpg")
        # 输入账号
        self.driver.find_element_by_xpath('//*[@id="account"]').send_keys("18124198818")
        # 输入密码
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys("dyly8818")
        # 点击登陆
        self.driver.find_element_by_xpath(
            '//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div/div[3]/div/a').click()
        time.sleep(2)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())
        self.driver.get("https://vip.xiniudata.com/org/investor/")
        time.sleep(2)
        size =os.path.getsize("dyly_spider/file/xiniudata")
        print(size)
        if size == 0:
            # 定义一个变量用与统计
            self.count = 0
            # 移动到底部 获取下一页数据
            while 1==1:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                # 获取列表数据
                li_list = self.driver.find_elements_by_xpath(
                    "//html/body/div/div/div[3]/div/div/div[2]/div/div[2]/section[1]/div/div/div/div/div[2]/div")
                time.sleep(10)
                # 获取下拉页有多少条数据
                self.cnt = len(li_list)
                if self.count == self.cnt:
                    break
                else:
                    self.count = self.cnt
            # 获取列表数据
            li_list = self.driver.find_elements_by_xpath(
                "//html/body/div/div/div[3]/div/div/div[2]/div/div[2]/section[1]/div/div/div/div/div[2]/div")
            file = open('dyly_spider/file/xiniudata', 'a')
            # 遍历读取写入文件
            for li in li_list:
                href = li.find_element_by_xpath(".//div[@class='jsx-1097797784 company-name']/div/a").get_attribute("href")
                print(href)
                file.write('\n'+href)
        # 读取文件中的路径，加载url，进入详情页
        else:
            cookies = self.driver.get_cookies()
            file = open("dyly_spider/file/xiniudata")
            for line in file:
                self.driver.get(line)
                time.sleep(2)
