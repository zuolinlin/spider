from dyly_spider.items import XiniuInstitutionItem, XiniuInvestmentEvents
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
                # 打开链接，加载数据
                self.driver.get(line)
                # 等在3s  让页面加载完成
                time.sleep(3)

                # 机构信息
                item = XiniuInstitutionItem()
                # 获取页面上的各个节点的信息
                # 机构logo
                item['logo'] = self.driver.find_element_by_xpath('//*[@id="header"]/div[1]/img').get_attribute("src")
                # 机构名称
                item['name'] = self.driver.find_element_by_xpath('//*[@id="header"]/div[2]/div[1]/span[1]').text
                # 机构的成立时间
                item['establishmentTime'] = self.driver.find_element_by_xpath('//*[@id="header"]/div[2]/div/span[2]').text
                # 机构描述
                item['describe'] = self.driver.find_element_by_xpath('//*[@id="header"]/div[2]/div[3]/div/pre').text
                # 插入机构主表 ，返回主键Id
                institutionId = self.insert("INSERT INTO `oltp`.`xiniu_institution_data` (`logo`, `name`,`establishmentTime`,`describe`) "
                       "VALUES (%s, %s,%s, %s)",
                       (item['logo'], item['name'], item['establishmentTime'], item['describe']))


                # 机构对应的投资信息
                inv = XiniuInvestmentEvents()
                # 获取页面上的各个节点的信息
                # 获取投资事件的列表的最大页数
                page_Last = self.driver.find_element_by_xpath(
                    '//*[@id="investorEvent"]/div[3]/div/div[2]/div[4]/div/div/ul/li[last() -1]').text
                num = 1
                while num < (int(page_Last)+1):
                    # 点击下一页
                    if num != 1:
                        new_list = self.driver.find_element_by_xpath(
                            '//*[@id="investorEvent"]/div[3]/div/div[2]/div[4]/div/div/ul/li[last()]').click()
                    num = num + 1
                    # 获取当前页的投资事件的列表信息
                    inv_list = self.driver.find_elements_by_xpath(
                        '//*[@id="investorEvent"]/div[3]/div/div[2]/div[3]/div/div/div[2]/div')
                    for invs in  inv_list:
                        inv['investmentTime'] = invs.find_element_by_xpath('div/div[1]').text
                        # 公司名称
                        inv['companyName'] = invs.find_element_by_xpath('div/div[2]/div/div[2]/div/a').text
                        # 公司logo
                        inv['companyLogo'] = invs.find_element_by_xpath('div/div[2]/div/div/a/img').get_attribute('src')
                        # 公司描述
                        inv['companyDescribe'] = invs.find_element_by_xpath('div/div[2]/div/div[2]/div[2]').text
                        # 行业领域
                        inv['industry'] = invs.find_element_by_xpath('div/div[3]').text
                        # 地区
                        inv['area'] = invs.find_element_by_xpath('div/div[4]').text
                        # 投资轮次
                        inv['currentTurn'] = invs.find_element_by_xpath('div/div[5]').text
                        # 投资金额
                        inv['amount'] = invs.find_element_by_xpath('div/div[6]').text
                        # 投资方
                        inv['investors'] = invs.find_element_by_xpath('div/div[7]/div').text
                        inv['institutionId'] = institutionId
                        print(inv)

                        self.driver.find_element_by_xpath('')
