from dyly_spider.spiders.BaseSpider import BaseSpider
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import uuid
"""
烯牛公司详情页数据 
"""


class XiniuCompanyDetailSpider(BaseSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "xiniuCompanyDetail"
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
        super(XiniuCompanyDetailSpider, self).__init__(*a, **kw)
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
        # self.driver = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
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
        time.sleep(5)
        # 从数据库中抓去
        pojo = self.fetchall("SELECT * FROM `xsbbiz`.`xiniu_company_data` limit 0,1000 ")
        len(pojo)
        for po in pojo:

            # 烯牛公司的主表信息  xiniu_company_data

            params = []
            companyId = po[0]
            detial = po[15]
            # 打开链接 睡5s
            self.driver.get(detial)
            time.sleep(3)
            # 获取详情页数据

            # 获取公司介绍数据 包含公司官网  ，公司描述，联系电话，邮箱 ，logo ，一句话介绍 所在地 成立时间
            try:
                city = self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[1]/span[4]').text  # 城市
            except:
                city = None

            try:
                website = self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[1]/a').get_attribute("href")  # 官网
            except:
                website = None

            try:
                description = self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[3]/div').text  # 公司描述
            except:
                description = None

            try:
                telephone = self.driver.find_element_by_xpath ('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[4]/div[1]/span').text  # 联系电话
            except:
                telephone = None
            try:
                email = self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[4]/div[2]/span').text  # 邮箱
            except:
                email = None

            try:
                foundingTime = self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div/div/div[3]/div[2]/div[1]/span[5]').text  # 成立时间
            except:
                foundingTime = None
            try:
                companyFullName =self.driver.find_element_by_xpath('//*[@id="gongshangInfo"]/div[3]/div[1]/span[2]').text  # 公司全称
            except:
                companyFullName = None
            try:
                legalRepresentative = self.driver.find_element_by_xpath('//*[@id="gongshangInfo"]/div[3]/div[2]/span[2]').text  # 法人代表
            except:
                legalRepresentative = None
            # 获取标签画像的数据
            try:
                advantages =self.driver.find_elements_by_xpath('//section[@id="tagInfo"]/div[3]/div[1]/div/a')  # 公司优势
                advantage = ""
                for i, tags in enumerate(advantages):
                    advantage = advantage + tags.text
                    if i != len(advantages) - 1:
                        advantage = advantage + "、"
            except:
                advantage = None
            try:
                industryClassifications =self.driver.find_elements_by_xpath('//section[@id="tagInfo"]/div[3]/div[2]/div/a') # 行业分类
                industryClassification = ""
                for i, tags in enumerate(industryClassifications):
                    industryClassification = industryClassification + tags.text
                    if i != len(industryClassifications) - 1:
                        industryClassification = industryClassification + "、"
            except:
                industryClassification = None
            params.append((
                companyFullName,
                telephone,
                email,
                website,
                foundingTime,
                city,
                advantage,
                industryClassification,
                legalRepresentative,
                description,
                companyId
            ))
            self.exec_sql("""
                        UPDATE 
                          `xsbbiz`.`xiniu_company_data`
                        SET
                          `companyFullName` =%s,
                          `telephone` =%s,
                          `email` =%s,
                          `website` =%s,
                          `foundingTime` =%s,
                          `city` =%s,
                          `advantage` =%s,
                          `industryClassification` =%s,
                          `legalRepresentative` =%s,
                          `description` =%s

                        WHERE `id` = %s 
                            """, (
                params
            ))
            # 公司成员信息
            member_params = []

            members = self.driver.find_elements_by_xpath(
                '//html/body/div/div/div[3]/div/section[@id="memberInfo"]/div[3]/div')  # 团队成员
            for member in members:
                ptotoUrl = member.find_element_by_xpath('./div/div/img').get_attribute("src")  # 姓名
                name = member.find_element_by_xpath('./div/div/strong').text  # 姓名
                position = member.find_element_by_xpath('./div/div/span[1]').text  # 职位
                university = member.find_element_by_xpath('./div/div/span[2]').text  # 毕业院校
                introduction = member.find_element_by_xpath('./div/pre').text  # 简介
                id = ''.join(str(uuid.uuid1()).split('-'))  # 主键
                member_params.append((
                    id,
                    ptotoUrl,
                    name,
                    position,
                    university,
                    introduction,
                    companyId

                ))

            # 插入sql
            self.insert("""
                         INSERT INTO `xsbbiz`.`xiniu_company_member_data` (`id`, `ptotoUrl`, `name` , `position`, `university`,`introduction` , `companyId`)
                         VALUES (%s, %s,%s,%s, %s,%s,%s)
                         """, member_params)

            # 公司招聘信息
            job_params = []
            jobs = self.driver.find_elements_by_xpath(
                '//html/body/div/div/div[3]/div/section[@id="jobInfo"]/div[2]/div/div/div/div/div[2]/div')  # 团队成员

            for job in jobs:
                updateTime = job.find_element_by_xpath("./div/div[1]").text  # 招聘时间
                positionName = job.find_element_by_xpath("./div/div[2]").text  # 职位
                city = job.find_element_by_xpath("./div/div[3]").text  # 地点
                workAreas = job.find_element_by_xpath("./div/div[4]").text  # 工作领域
                educationalLevel = job.find_element_by_xpath("./div/div[5]").text  # 教育要求
                id = ''.join(str(uuid.uuid1()).split('-'))  # 主键
                job_params.append((
                    id,
                    updateTime,
                    positionName,
                    city,
                    workAreas,
                    educationalLevel,
                    companyId
                ))

            # 插入sql
            self.insert("""
                         INSERT INTO `xsbbiz`.`xiniu_company_recruit_data` (`id`, `updateTime`, `positionName` , `city`, `workAreas`,`educationalLevel` , `companyId`)
                         VALUES (%s, %s,%s,%s, %s,%s,%s)
                         """, job_params)


            # 相关新闻
            news_params = []
            jobs = self.driver.find_elements_by_xpath(
                '//html/body/div/div/div[3]/div/div[@id="newsInfo"]/select[id ="news"]/')  # 团队成员

    pass
