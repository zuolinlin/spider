from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import datetime
from util import CookieUtil, date_util, QiniuUtil
import re
import uuid

"""
烯牛资讯业数据--只爬取最新的数据，可设置定时爬取
"""


class XiniuNewsSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuNews"
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
        super(XiniuNewsSpider, self).__init__(*a, **kw)
        self.url = "http://www.xiniudata.com"
        self.chrome_options = Options()
        #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
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
        XiniuNewsSpider.sysnc_new(self)
       # XiniuNewsSpider.do_news(self)

    def sysnc_new(self):
        self.driver.get("http://www.xiniudata.com/info/news/lib")
        time.sleep(2)
        # 获取咨询表中的数据
        # pojo = self.fetchall("SELECT * FROM `xsbbiz`.`xiniu_news` limit 1 ")
        # 现将新闻列表页的数据入库 ，
        start = 20
        while 1==1:
            # 下拉加载
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)
            #  获取 列表页数据
            news_data = self.driver.find_elements_by_xpath('//html/body/div/div/div/div[2]/div/div/div/div[2]/div/div[2]/section/div/div')

            length = len(news_data)

            if start == length:
                news_data = news_data[(start -100):start]
                start =start + 100
                params = []
                for new_data in news_data:
                    # print((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))
                    # print((datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"))
                    # print((datetime.datetime.now() - datetime.timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M"))
                    # times = new_data.find_element_by_xpath('./span').text  # 烯牛对应的详情页的URl
                    # dataTime = None
                    # ti = times[-2:]
                    # if ti == "时前":
                    #     houses = times[0:-3]
                    #     dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime("%Y-%m-%d %H:%M")
                    # elif ti == "天前":
                    #     days = times[0:-2]
                    #     dataTime =(datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
                    # elif ti == "周前":
                    #     print("333")
                    # elif ti == "周前":
                    #     print(".....")
                    # else:
                    #     print(".....")

                    xnDetialUrl = new_data.find_element_by_xpath('./div/a').get_attribute('href')  # 烯牛对应的详情页的URl
                    id = xnDetialUrl[30:]
                    params.append((
                        id,
                        xnDetialUrl
                    ))
                # 插入sql
                self.insert("""
                             INSERT INTO `xsbbiz`.`xiniu_news` (`id`, `xndetialUrl`) 
                             VALUES (%s,%s)
                             """,params)
            else:
                continue

    def do_news(self):
        news = self.fetchall("SELECT * FROM `xsbbiz`.`xiniu_news` limit 1259 ,2000 ")
        for new in news:
            newsId = new[0]     #新闻Id
            xnDetialUrl = new[9]  # 烯牛详情页对应的URl
            # 打开详情页
            self.driver.get(xnDetialUrl)

            params = []

            # 相关行业
            advantage =""
            try:
                industry_names = self.driver.find_elements_by_xpath('//Html/body//div[@class = "industry-name"]')
                for i, tags in enumerate(industry_names):
                    advantage = advantage + tags.text
                    if i != len(industry_names) - 1:
                        advantage = advantage + "、"
            except:
                advantage = advantage

            title =self.driver.find_element_by_xpath('//html/body/div/div/div/div[2]/div/div/div[1]/div[@class="news-detail"]/div[@class= "news-title"]').text
            classify = self.driver.find_element_by_xpath(
                '//html/body/div/div/div/div[2]/div/div/div[1]/div[@class="news-detail"]/div[@class= "news-info"]/span[1]').text  # 分类
            newstime = self.driver.find_element_by_xpath(
                '//html/body/div/div/div/div[2]/div/div/div[1]/div[@class="news-detail"]/div[@class= "news-info"]/span[2]').text  # 新闻时间
            ti = newstime[-2:]
            if ti == "时前":
                houses = newstime[5:-3]
                dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(houses))).strftime("%Y-%m-%d %H:%M")
            elif ti == "天前":
                days = newstime[5:-2]
                dataTime =(datetime.datetime.now() - datetime.timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M")
            elif ti == "钟前":
                minute = newstime[5:-3]
                dataTime = (datetime.datetime.now() - datetime.timedelta(minutes=int(minute))).strftime("%Y-%m-%d %H:%M")
            elif ti == "周前":
                print(".....")
            else:
                dataTime = newstime[5:]

            source = self.driver.find_element_by_xpath(
                '//html/body/div/div/div/div[2]/div/div/div[1]/div[@class="news-detail"]/div[@class= "news-info"]/span[3]/a').text  # 来源
            linkUrl = self.driver.find_element_by_xpath(
                                '//html/body/div/div/div/div[2]/div/div/div[1]/div[@class="news-detail"]/div[@class= "news-info"]/span[3]/a').get_attribute('href')  # 来源URl

            html = self.driver.find_element_by_xpath(
                '//Html/body/div/div/div/div[2]/div/div/div[1]/div/div[@class= "news-content"]').get_attribute("outerHTML")

            # 设置富文本内容，如果有图片 将图片转存到七牛的文件服务器上
            try:
                # 判断新闻的内容有没有引用图片
                imgs = self.driver.find_elements_by_xpath('//Html/body/div/div/div/div[2]/div/div/div[1]/div/div[@class= "news-content"]//img')
                for img in imgs:
                    src = img.get_attribute("src")
                    imgId = src[30:]
                    newUrls = QiniuUtil.upload(src, imgId, "png")
                    newUrl = newUrls[0]
                    new = str(newUrl)
                    old = str(src)
                    strinfo = re.compile(old)
                    html = strinfo.sub(new, html)
                    print(html)
            except:
                self.log(newsId +" 新闻内容没有图片" )
            params.append((
                title,
                dataTime,
                classify,
                source,
                linkUrl,
                advantage,
                html,
                newsId
            ))
            self.exec_sql("""
                              UPDATE 
                                `xsbbiz`.`xiniu_news`
                              SET
                                `title` =%s,
                                `time` =%s,
                                `classify` =%s,
                                `source` =%s,
                                `linkUrl` =%s,
                                `relatedIndustries` =%s,
                                `contents` =%s
                              WHERE `id` = %s 
                                  """, (
                params
            ))


            # 将关联的数据入库
            # 相关公司
            relation_params = []
            try:
                company_names = self.driver.find_elements_by_xpath('//Html/body//div[@class= "company-name"]//a')
                for company_name in company_names:
                    id = ''.join(str(uuid.uuid1()).split('-'))
                    type ="2"
                    company_url = company_name.get_attribute("href")
                    companyId = company_url[33:-9]
                    relation_params.append((
                        id,
                        type,
                        newsId,
                        companyId
                    ))
            except:
                self.log(newsId + "无关联公司")


            # 相关机构
            try:
                investor_names = self.driver.find_elements_by_xpath(
                    '//Html/body//div[@class="name"]/a')
                for investor_name in investor_names:
                    id = ''.join(str(uuid.uuid1()).split('-'))
                    type = "1"
                    investor_url = investor_name.get_attribute("href")
                    investorId = investor_url[34:-9]
                    relation_params.append((
                        id,
                        type,
                        newsId,
                        investorId
                    ))
            except:
                self.log(newsId + "无关联机构")

            if len(relation_params) != 0:
                # 插入sql
                self.insert("""
                                INSERT INTO `xsbbiz`.`xiniu_news_relation_data` (`id`, `type`,`newsId`, `objectId`) 
                                VALUES (%s,%s,%s,%s)
                                """, relation_params)





