from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import datetime
from util import CookieUtil, date_util, QiniuUtil
import re
import uuid
"""
烯牛的研报数据
"""


class XiniuReportSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuReport"
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
        super(XiniuReportSpider, self).__init__(*a, **kw)
        self.url = "http://www.xiniudata.com"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

        # chrome_options = webdriver.ChromeOptions()
        # # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        # self.driver = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
        #                                chrome_options=chrome_options)
        self.driver.get(self.url)
        time.sleep(3)  # 睡3毫秒，等待页面加载
        # self.driver.save_screenshot("0.jpg")
        # # 输入账号
        # self.driver.find_element_by_xpath('//*[@id="account"]').send_keys("17621785089")
        # # 输入密码
        # self.driver.find_element_by_xpath('//*[@id="password"]').send_keys("lll123456")
        # # 点击登陆
        # self.driver.find_element_by_xpath(
        #     '//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[3]/div/div[3]/div/a').click()
        # time.sleep(10)
        # 输出登陆之后的cookies
        print(self.driver.get_cookies())
        # XiniuReportSpider.do_Report(self)
        XiniuReportSpider.upload_pdf(self)

        #  打开链接
        self.driver.get("http://www.xiniudata.com/report")
        time.sleep(3)
        source = 1
        sum = 0
        # 烯牛研报只提供最新的前100 页的数据
        for n in range(1, 5):
            # 获取分页栏的数据
            page_list = self.driver.find_elements_by_xpath('//Html/body/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/div/div/ul/li')
            for page in page_list:
                flag = page.find_element_by_xpath('./a').text
                if str(flag) == str(n):
                    page.click()
                    time.sleep(3)
                    break
            sum = sum + n
            #  获取当前页面的列表页数据
            data_report = self.driver.find_elements_by_xpath('//Html/body/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/div/section/div[2]/div')
            if len(data_report) != 0:
                params = []
                for report in data_report:
                    publishTime = report.find_element_by_xpath('./div/div[1]').text  # 时间
                    ti =publishTime[-2:]
                    if ti == "时前":
                        houses = publishTime[0:-3]
                        date_str = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime(
                            "%Y-%m-%d %H:%M")
                    elif ti == "天前":
                        days = publishTime[0:-2]
                        date_str = (datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime(
                            "%Y-%m-%d %H:%M")
                    elif ti == "钟前":
                        minute = publishTime[0:-3]
                        date_str = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime(
                            "%Y-%m-%d %H:%M")
                    elif ti == "周前":
                        print(".....")
                    else:
                        date_str = publishTime
                    title = report.find_element_by_xpath('./div/div[2]/a').text  # 标题
                    herf = report.find_element_by_xpath('./div/div[2]/a').get_attribute('href')
                    report_id = str(herf).split('/')[5]
                    # url, pdfsize = QiniuUtil.upload(herf, "xiniu-" + str(report_id), "pdf")
                    try:
                        page_large = report.find_element_by_xpath('./div/div[3]').text  # 总页书，以及文件大小
                        page_lars = str(page_large).split(' ')
                        fileSize = float(page_lars[0][0:-2]) * 1024  # 将文件转换为KB 文件大小
                        pageCount =page_lars[1].replace("页）", '').replace('（', '')  # 文件页数
                        pageCount =int(pageCount)
                    except:
                        continue
                    org_name = report.find_element_by_xpath('./div/div[4]').text   # 来源
                    now = time.localtime()
                    params.append((
                        report_id,
                        source,
                        title,
                        date_str,
                        org_name,
                        pageCount,
                        herf,
                        fileSize,
                        now
                    ))
                    # 插入sql
                    self.insert("""
                                   INSERT INTO `robo_report` (
                                     `report_id`,
                                     `source`,
                                     `title`,
                                     `publish_time`,
                                     `org_name`,
                                     `pageCount`,
                                     `pdf`,
                                     `size`,
                                     `modify_date`
                                   )
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                   """, params)

    def upload_pdf(self):
        reports = self.fetchall("SELECT * FROM `xsbbiz`.`robo_report` where  source = 1 ")
        for report in reports:
            report_id = report[0]
            src =report[9]
            url, pdfsize = QiniuUtil.upload(src, "xiniu-" + str(report_id), "pdf")
            self.exec_sql("""
                              UPDATE 
                                `xsbbiz`.`robo_report`
                              SET
                                `pdf` =%s
                              WHERE `report_id` = %s 
                                  """, (
                url,
                report_id

            ))

