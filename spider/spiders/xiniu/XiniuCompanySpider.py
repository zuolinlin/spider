from spider.items import XiniuCompany
from spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

""""
烯牛公司的列表页数据将所有的公司的数据全部拉取下来----未去重（后续可以自己去重即可）
"""


class XiniuCompanySpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniucompany"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["https://vip.xiniudata.com"]
    #  开始爬取的地址
    start_urls = ['https://vip.xiniudata.com']

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
    }

    #  设置登陆，
    def __init__(self, *a, **kw):
        super(XiniuCompanySpider, self).__init__(*a, **kw)
        self.url = "https://vip.xiniudata.com"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
        #                                chrome_options=chrome_options)
        self.driver.get(self.url)
        time.sleep(3)  # 睡3毫秒，等待页面加载
        # self.driver.save_screenshot("0.jpg")
        # 输入账号
        self.driver.find_element_by_xpath('//*[@id="account"]').send_keys("13760461032")
        # 输入密码
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys("dyly123456")
        # 点击登陆
        self.driver.find_element_by_xpath(
            '//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div/div[3]/div/a').click()
        time.sleep(3)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())
        self.driver.get("https://vip.xiniudata.com/project/lib")
        pojo = self.fetchall("SELECT * FROM `xsbbiz`.`xiniu_company_data` ")
        len(pojo)
        # 将烯牛的列表页的数据入库
        if pojo is None or len(pojo) == 0:
            # 定义一个变量用与统计
            self.count = 0
            # 移动到底部 获取下一页数据
            while 1 == 1:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(5)
                # 获取列表数据
                li_list = self.driver.find_elements_by_xpath(
                    "//html/body/div/div/div[3]/div/div/div[2]/div/div[2]/section[1]/div/div/div/div/div[2]/div")

                # 定义一个变量用与统计
                self.count = 0
                # 每当获取的100 页时 ，取最后的100条的数据存库，然后继续下拉加载
                flg = len(li_list)
                if flg % 100 == 0:
                    params = []
                    # 获取列表页的最后的100条数据
                    start = flg - 100
                    li_list =li_list[start:]
                    for i, val in enumerate(li_list, start):
                        xiniuCompany = XiniuCompany()
                        xiniuCompany['companyAbbreviation'] = val.find_element_by_xpath("./div/div[2]/div/div[2]/div/a").text  # 公司简称
                        xiniuCompany['logoUrl'] = val.find_element_by_xpath("./div/div[2]/div/div/a/img").get_attribute("src")   # logo
                        url = val.find_element_by_xpath("./div/div[2]/div/div[2]/div/a").get_attribute("href")  # 详情页url
                        id = url[34:-9]
                        xiniuCompany['url'] =url
                        xiniuCompany['id'] = id
                        xiniuCompany['inaword'] = val.find_element_by_xpath("./div/div[2]/div/div[2]/div[2]").text  # 一句话介绍
                        params.append((
                            xiniuCompany['id'],
                            xiniuCompany['logoUrl'],
                            xiniuCompany['companyAbbreviation'],
                            xiniuCompany['inaword'],
                            xiniuCompany['url']
                        ))

                    # 插入sql
                    self.insert("""
                                  INSERT INTO `xsbbiz`.`xiniu_company_data` (`id`,`logoUrl`,`companyAbbreviation`,`inaword`, `url`) 
                                  VALUES (%s,%s, %s,%s, %s)
                                  """,
                                params)
                else:
                    # 获取下拉页有多少条数据
                    self.cnt = len(li_list)
                    # 如果已经下拉到最后一页  ，获取下拉列表的
                    if self.count == self.cnt:
                        # 插入最后的数据 跳出
                        break
                    else:
                        self.count = self.cnt

        else:
            print("-===")







