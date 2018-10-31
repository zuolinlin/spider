from dyly_spider.items import XiniuInstitutionItem, XiniuInvestmentEvents, XiniuInstitudynamic, XiniuNews, XiniuFun, \
    XiniuFundmanager, XiniuLP
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
        # self.chrome_options = Options()
        # #  设置浏览器是否隐藏
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')
        self.driver = webdriver.Chrome(executable_path=r'dyly_spider/file/chromedriver.exe',
                                       chrome_options=chrome_options)
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
        time.sleep(10)
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
                #self.driver.get("https://vip.xiniudata.com/investor/01924fdebe4b58081eeff15293b1db52/overview")
                # 等在3s  让页面加载完成
                time.sleep(10)
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

                # institutionId =int(id)
                # 机构对应的投资信息
                flag10 = True
                try:
                    self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/section[@id="investorEvent"]')
                    flag10 = flag10
                except:
                    flag10 = False
                # 如果机构动态数据列表数据这个div 存在
                if flag10:
                    inv = XiniuInvestmentEvents()
                    # 判断页面是否有下一页的按钮
                    flag11 = True
                    try:
                        self.driver.find_element_by_xpath(
                            '//*[@id="investorEvent"]/div[3]/div/div[2]/div[4]/div/div/ul/li[last()]')
                        flag11 = flag11
                    except:
                        flag11 = False
                    # 如果有下一页的按钮
                    if flag11:
                        # 获取页面上的各个节点的信息
                        # 获取投资事件的列表的最大页数
                        page_Last = self.driver.find_element_by_xpath(
                            '//*[@id="investorEvent"]/div[3]/div/div[2]/div[4]/div/div/ul/li[last() -1]').text
                        num = 1
                        while num < (int(page_Last)+1):
                            # 点击下一页
                            if num != 1:
                                try:

                                    new_list = self.driver.find_element_by_xpath(
                                        '//*[@id="investorEvent"]/div[3]/div/div[2]/div[4]/div/div/ul/li[last()]').click()
                                    time.sleep(6)
                                except:
                                    self.log("====处理失败的URL"+line+"投资信息失败")
                                    break
                            num = num + 1
                            # 获取当前页的投资事件的列表信息
                            inv_list = self.driver.find_elements_by_xpath(
                                '//*[@id="investorEvent"]/div[3]/div/div[2]/div[3]/div/div/div[2]/div')
                            params = []
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
                                params.append((
                                    inv['investmentTime'],
                                    inv['companyName'],
                                    inv['companyLogo'],
                                    inv['companyDescribe'],
                                    inv['industry'],
                                    inv['area'],
                                    inv['currentTurn'],
                                    inv['amount'],
                                    inv['investors'],
                                    inv['institutionId']
                                ))
                            # 插入sql
                            invId = self.insert("""
                                                     INSERT INTO `oltp`.`xiniu_investmentevents_data` (`investmentTime`, `companyName`,`companyLogo`,`companyDescribe`,`industry`,`area`,`currentTurn`,`amount`,`investors`,`institutionId`) 
                                                     VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)
                                                     """,
                                                params)
                    else:
                        # 获取当前页的投资事件的列表信息
                        inv_list = self.driver.find_elements_by_xpath(
                            '//*[@id="investorEvent"]/div[3]/div/div[2]/div[3]/div/div/div[2]/div')
                        for invs in inv_list:
                            inv['investmentTime'] = invs.find_element_by_xpath('div/div[1]').text
                            # 公司名称
                            inv['companyName'] = invs.find_element_by_xpath('div/div[2]/div/div[2]/div/a').text
                            # 公司logo
                            inv['companyLogo'] = invs.find_element_by_xpath('div/div[2]/div/div/a/img').get_attribute(
                                'src')
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
                            # 插入sql
                            invId = self.insert(
                                "INSERT INTO `oltp`.`xiniu_investmentevents_data` (`investmentTime`, `companyName`,`companyLogo`,`companyDescribe`,`industry`,`area`,`currentTurn`,`amount`,`investors`,`institutionId`) "
                                "VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)",
                                (inv['investmentTime'], inv['companyName'], inv['companyLogo'], inv['companyDescribe'],
                                 inv['industry'], inv['area'], inv['currentTurn'], inv['amount'], inv['investors'],
                                 inv['institutionId']))

                #  判断这个机构动态数据列表div是否存在
                flag1 = True
                try:
                    self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/section[@id="investorMessage"]')
                    flag1 = flag1
                except:
                    flag1 = False
                # 如果机构动态数据列表数据这个div 存在
                if flag1:
                # 烯牛抓去机构动态数据列表数据
                    dyna = XiniuInstitudynamic()
                    #判断页面是否有下一页的按钮
                    flag2 = True
                    try:
                        self.driver.find_element_by_xpath(
                            '//*[@id="investorMessage"]/div[2]/div[2]/div[3]/div/div/ul/li[last() -1]')
                        flag2= flag2
                    except:
                        flag2 = False
                    # 如果有下一页的按钮
                    if flag2:
                        # 获取动态事件的最大页数
                        dyna_page_Last = self.driver.find_element_by_xpath(
                            '//*[@id="investorMessage"]/div[2]/div[2]/div[3]/div/div/ul/li[last() -1]').text
                        num = 1
                        while num < (int(dyna_page_Last) + 1):
                            # 点击下一页
                            if num != 1:
                                try:
                                    new_list = self.driver.find_element_by_xpath(
                                        '//*[@id="investorMessage"]/div[2]/div[2]/div[3]/div/div/ul/li[last()]').click()
                                    time.sleep(6)
                                except:
                                    self.log("====处理失败的URL" + line + "动态事件")
                                    break
                            num = num + 1
                            # 获取列表页的数据
                            dyna_data = self.driver.find_elements_by_xpath(
                                '//*[@id="investorMessage"]/div[2]/div[2]/div[2]/div/div/div[2]/div')
                            params = []
                            for dynas in dyna_data:
                                # 动态时间
                                dyna['dynamicTime'] = dynas.find_element_by_xpath('div/div').text
                                # 动态类型
                                dyna['dynamicType'] = dynas.find_element_by_xpath('div/div[2]').text
                                # 内容
                                dyna['content'] = dynas.find_element_by_xpath('div/div[3]').text
                                # # 关键字
                                # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                                dyna['institutionId'] = institutionId
                                params.append((
                                    dyna['dynamicTime'],
                                    dyna['dynamicType'],
                                    dyna['content'],
                                    dyna['institutionId']

                                ))
                            # 插入sql
                            dynaId = self.insert(
                                """INSERT INTO `oltp`.`xiniu_institudynamic_data` (`dynamicTime`, `dynamicType`,`content`,`institutionId`) 
                                VALUES (%s, %s,%s,%s)""",
                                params)
                         # 没有下一页的按钮 ，直接获取列表也数据
                        else:
                            # 获取列表页的数据
                            dyna_data = self.driver.find_elements_by_xpath(
                                '//*[@id="investorMessage"]/div[2]/div[2]/div[2]/div/div/div[2]/div')

                            for dynas in dyna_data:
                                # 动态时间
                                dyna['dynamicTime'] = dynas.find_element_by_xpath('div/div').text
                                # 动态类型
                                dyna['dynamicType'] = dynas.find_element_by_xpath('div/div[2]').text
                                # 内容
                                dyna['content'] = dynas.find_element_by_xpath('div/div[3]').text
                                # # 关键字
                                # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                                dyna['institutionId'] = institutionId
                                # 插入sql
                                dynaId = self.insert(
                                    "INSERT INTO `oltp`.`xiniu_institudynamic_data` (`dynamicTime`, `dynamicType`,`content`,`institutionId`) "
                                    "VALUES (%s, %s,%s,%s)",
                                    (dyna['dynamicTime'], dyna['dynamicType'], dyna['content'], dyna['institutionId']))

                #  判断这个新闻div是否存在
                flag3 = True
                try:
                    self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/div[@id="investorNews"]')
                    flag3 = flag3
                except:
                    flag3 = False
                # 如果新闻列表数据这个div 存在
                if flag3:
                    # 烯牛抓去机构新闻列表数据
                    new = XiniuNews()
                     # 烯牛抓去机构详情相关的新闻数据
                     # 获取机构新闻页的当前页数据，目前只能获取到第一页，后面如果在能获取在做调整
                     # 获取列表页的数据
                    news_data = self.driver.find_elements_by_xpath(
                        '//html/body/div/div/div[3]/div/div[3]/section[@id="news"]/div[2]/div/ol/li')
                    for news in news_data:
                        # 新闻事件
                        new['newsTime'] = news.find_element_by_xpath('div/div/div').text
                        # 来源
                        new['source1'] = news.find_element_by_xpath('div/div/div[2]/div/span[1]').text
                        # 来源
                        new['source2'] = news.find_element_by_xpath('div/div/div[2]/div/span[2]').text
                        # 标题
                        new['title'] = news.find_element_by_xpath('div/div/div[2]/div[2]/a/span').text
                        # 新闻地址
                        new['url'] = news.find_element_by_xpath('div/div/div[2]/div[2]/a').get_attribute('href')
                        new['institutionId'] = institutionId
                        # 插入sql
                        newId = self.insert(
                            "INSERT INTO `oltp`.`xiniu_news_data` (`newsTime`, `source1`,`source2`,`title`,`url`,`institutionId`) "
                            "VALUES (%s, %s,%s, %s,%s,%s)",
                            (new['newsTime'], new['source1'], new['source2'], new['title'], new['url'], new['institutionId']))


                #  判断这个基金div是否存在
                flag4 = True
                try:
                    self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/section[@id="investorFund"]')
                    flag4 = flag4
                except:
                    flag4 = False
                if flag4:

                    # 管理基金列表
                    fun = XiniuFun()
                    flag5 = True
                    try:
                        self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFund"]/div[2]/div/div[3]/div/div/ul/li[last()]')
                        flag5 = flag5
                    except:
                        flag5 =False
                    if flag5:
                        # 获取动态事件的最大页数
                        fun_page_Last = self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFund"]/div[2]/div/div[3]/div/div/ul/li[last() -1]').text
                        num = 1
                        while num < (int(fun_page_Last) + 1):
                            # 点击下一页
                            if num != 1:
                                try:
                                    new_list = self.driver.find_element_by_xpath(
                                        '//html/body/div/div/div[3]/div/section[@id="investorFund"]/div[2]/div/div[3]/div/div/ul/li[last()]').click()
                                    time.sleep(6)
                                except:
                                    self.log("====处理失败的URL" + line + "基金信息失败")
                                    break
                            params = []
                            num = num + 1
                            # 获取列表页的数据
                            fun_data = self.driver.find_elements_by_xpath(
                                '//html/body/div/div/div[3]/div/section[@id="investorFund"]/div[2]/div/div[2]/div/div/div[2]/div')

                            for funs in fun_data:
                                # 备案时间
                                fun['recordTime'] = funs.find_element_by_xpath('div/div').text
                                # 基金名称
                                fun['fundName'] = funs.find_element_by_xpath('div/div[2]/div').text
                                # url
                                try:
                                     fun['url'] = funs.find_element_by_xpath('div/div[2]/div/a').get_attribute('href')
                                except:
                                    fun['url'] =""
                                # 注册资本
                                fun['registeredCapita'] = funs.find_element_by_xpath('div/div[3]').text
                                # 执行事务合伙人
                                fun['partner'] = funs.find_element_by_xpath('div/div[4]').text
                                #  工商成立时间
                                fun['foundingTime'] = funs.find_element_by_xpath('div/div[5]').text
                                # # 关键字
                                # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                                fun['institutionId'] = institutionId
                                params.append((
                                    fun['recordTime'],
                                    fun['fundName'],
                                    fun['url'],
                                    fun['registeredCapita'],
                                    fun['partner'],
                                    fun['foundingTime'],
                                    fun['institutionId']

                                ))

                            # 插入sql
                            funId = self.insert(
                                """
                                INSERT INTO `oltp`.`xiniu_fund_data` (`recordTime`, `fundName`,`url`,`registeredCapita`,`partner`,`foundingTime` ,`institutionId`)
                                VALUES (%s, %s,%s, %s,%s, %s,%s)
                                """,
                                params)
                    else:
                        # 获取列表页的数据
                        fun_data = self.driver.find_elements_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFund"]/div[2]/div/div[2]/div/div/div[2]/div')

                        for funs in fun_data:
                            # 备案时间
                            fun['recordTime'] = funs.find_element_by_xpath('div/div').text
                            # 基金名称
                            fun['fundName'] = funs.find_element_by_xpath('div/div[2]/div').text
                            # url
                            fun['url'] = funs.find_element_by_xpath('div/div[2]/div/a').get_attribute('href')
                            # 注册资本
                            fun['registeredCapita'] = funs.find_element_by_xpath('div/div[3]').text
                            # 执行事务合伙人
                            fun['partner'] = funs.find_element_by_xpath('div/div[4]').text
                            #  工商成立时间
                            fun['foundingTime'] = funs.find_element_by_xpath('div/div[5]').text
                            # # 关键字
                            # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                            fun['institutionId'] = institutionId
                            # 插入sql
                            funId = self.insert(
                                "INSERT INTO `oltp`.`xiniu_fund_data` (`recordTime`, `fundName`,`url`,`registeredCapita`,`partner`,`foundingTime` ,`institutionId`)"
                                "VALUES (%s, %s,%s, %s,%s, %s,%s)",
                                (fun['recordTime'], fun['fundName'], fun['url'], fun['registeredCapita'],
                                 fun['partner'],
                                 fun['foundingTime'], fun['institutionId']))

                    #  判断这个基金管理人列表div是否存在
                flag6 = True
                try:
                    self.driver.find_element_by_xpath('//html/body/div/div/div[3]/div/section[@id="investorFundManager"]')
                    flag6 = flag6
                except:
                    flag6 = False
                if flag6:

                    # 管理基金管理人列表
                    fundmanager = XiniuFundmanager()
                    flag7 = True
                    try:
                        self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFundManager"]/div[2]/div/div/div[3]/div/div/ul/li[last()]')
                        flag7 = flag7
                    except:
                        flag7 = False
                    if flag7:
                        # 获取基金管理人的最大页数
                        fun_page_Last = self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFundManager"]/div[2]/div/div/div[3]/div/div/ul/li[last() -1]').text
                        num = 1
                        while num < (int(fun_page_Last) + 1):
                            # 点击下一页
                            if num != 1:
                                try:
                                    new_list = self.driver.find_element_by_xpath(
                                     '//html/body/div/div/div[3]/div/section[@id="investorFundManager"]/div[2]/div/div/div[3]/div/div/ul/li[last()]').click()
                                    time.sleep(6)
                                except:
                                    self.log("====处理失败的URL" + line + "基金管理人失败")
                                    break
                            params = []
                            num = num + 1
                            # 获取列表页的数据
                            fun_data = self.driver.find_elements_by_xpath(
                                '//html/body/div/div/div[3]/div/section[@id="investorFundManager"]/div[2]/div/div/div[2]/div/div/div[2]/div')

                            for funs in fun_data:
                                # 成立时间
                                fundmanager['foundingTime'] = funs.find_element_by_xpath('div/div').text
                                # 基金名称
                                fundmanager['name'] = funs.find_element_by_xpath('div/div[2]').text
                                # 法人代表
                                fundmanager['legalRepresentative'] = funs.find_element_by_xpath('div/div[3]').text
                                # 管理基金
                                fundmanager['managementFund'] = funs.find_element_by_xpath('div/div[4]').text
                                # 基金备案时间
                                fundmanager['recordTime'] = funs.find_element_by_xpath('div/div[5]').text
                                # # 关键字
                                # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                                fundmanager['institutionId'] = institutionId

                                params.append((
                                    fundmanager['foundingTime'],
                                    fundmanager['name'],
                                    fundmanager['legalRepresentative'],
                                    fundmanager['managementFund'],
                                    fundmanager['recordTime'],
                                    fundmanager['institutionId']

                                ))
                            # 插入sql
                            fundmanagerId = self.insert(
                                """INSERT INTO `oltp`.`xiniu_fundmanager_data` (`foundingTime`, `name`,`legalRepresentative`,`managementFund`,`recordTime`,`institutionId` )
                                VALUES (%s, %s,%s, %s,%s, %s)
                                """,
                                params)
                    else:
                        # 获取列表页的数据
                        fun_data = self.driver.find_elements_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorFundManager"]/div[2]/div/div/div[2]/div/div/div[2]/div')

                        for funs in fun_data:
                            # 成立时间
                            fundmanager['foundingTime'] = funs.find_element_by_xpath('div/div').text
                            # 基金名称
                            fundmanager['name'] = funs.find_element_by_xpath('div/div[2]').text
                            # 法人代表
                            fundmanager['legalRepresentative'] = funs.find_element_by_xpath('div/div[3]').text
                            # 管理基金
                            fundmanager['managementFund'] = funs.find_element_by_xpath('div/div[4]').text
                            # 基金备案时间
                            fundmanager['recordTime'] = funs.find_element_by_xpath('div/div[5]').text
                            # # 关键字
                            # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                            fundmanager['institutionId'] = institutionId
                            # 插入sql
                            fundmanagerId = self.insert(
                                "INSERT INTO `oltp`.`xiniu_fundmanager_data` (`foundingTime`, `name`,`legalRepresentative`,`managementFund`,`recordTime`,`institutionId` )"
                                "VALUES (%s, %s,%s, %s,%s, %s)",
                                (fundmanager['foundingTime'], fundmanager['name'], fundmanager['legalRepresentative'],
                                 fundmanager['managementFund'], fundmanager['recordTime'],
                                 fundmanager['institutionId']))

                #  判断这个LP 列表数据div是否存在
                flag8 = True
                try:
                    self.driver.find_element_by_xpath(
                        '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]')
                    flag8 = flag8
                except:
                    flag8 = False
                if flag8:
                    # LP 列表数据
                    xiniuLP = XiniuLP()
                    flag9 = True
                    try:
                        self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]/div[2]/div/div/div[3]/div/div/ul/li[last()]')
                        flag9 = flag9
                    except:
                        flag9 = False
                    if flag9:
                        # 获取动态事件的最大页数
                        fun_page_Last = self.driver.find_element_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]/div[2]/div/div/div[3]/div/div/ul/li[last() -1]').text
                        num = 1
                        while num < (int(fun_page_Last) + 1):
                            # 点击下一页
                            if num != 1:
                                try:
                                    new_list = self.driver.find_element_by_xpath(
                                     '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]/div[2]/div/div/div[3]/div/div/ul/li[last()]').click()
                                    time.sleep(6)
                                except:
                                    self.log("====处理失败的URL" + line + "LP失败")
                                    break
                            params = []
                            num = num + 1
                            # 获取列表页的数据
                            fun_data = self.driver.find_elements_by_xpath(
                                '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]/div[2]/div/div/div[2]/div/div/div[2]/div')

                            for funs in fun_data:
                                # Lp名称
                                xiniuLP['lpName'] = funs.find_element_by_xpath('div/div').text
                                # 归属机构
                                xiniuLP['ownershipOrganization'] = funs.find_element_by_xpath('div/div[2]').text
                                # 参与基金数
                                xiniuLP['fundsNum'] = funs.find_element_by_xpath('div/div[3]').text
                                # 其它合作机构
                                xiniuLP['cooperationAgency'] = funs.find_element_by_xpath('div/div[4]').text
                                # # 关键字
                                # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                                xiniuLP['institutionId'] = institutionId
                                params.append((
                                    xiniuLP['lpName'],
                                    xiniuLP['ownershipOrganization'],
                                    xiniuLP['fundsNum'],
                                    xiniuLP['cooperationAgency'],
                                    xiniuLP['institutionId']

                                ))
                            # 插入sql
                            xiniuLPId = self.insert(
                                """
                                INSERT INTO `oltp`.`xiniu_lp_data` (`lpName`, `ownershipOrganization`,`fundsNum`,`cooperationAgency`,`institutionId` )
                                VALUES (%s, %s,%s, %s,%s)
                                """,
                                params)
                    else:
                        # 获取列表页的数据
                        fun_data = self.driver.find_elements_by_xpath(
                            '//html/body/div/div/div[3]/div/section[@id="investorPartnerLP"]/div[2]/div/div/div[2]/div/div/div[2]/div')

                        for funs in fun_data:
                            # Lp名称
                            xiniuLP['lpName'] = funs.find_element_by_xpath('div/div').text
                            # 归属机构
                            xiniuLP['ownershipOrganization'] = funs.find_element_by_xpath('div/div[2]').text
                            # 参与基金数
                            xiniuLP['fundsNum'] = funs.find_element_by_xpath('div/div[3]').text
                            # 其它合作机构
                            xiniuLP['cooperationAgency'] = funs.find_element_by_xpath('div/div[4]').text
                            # # 关键字
                            # dyna['keyWord'] = dynas.find_element_by_xpath('div/div[3]/a').text
                            xiniuLP['institutionId'] = institutionId
                            # 插入sql
                            xiniuLPId = self.insert(
                                "INSERT INTO `oltp`.`xiniu_lp_data` (`lpName`, `ownershipOrganization`,`fundsNum`,`cooperationAgency`,`institutionId` )"
                                "VALUES (%s, %s,%s, %s,%s)",
                                (xiniuLP['lpName'], xiniuLP['ownershipOrganization'], xiniuLP['fundsNum'],
                                 xiniuLP['cooperationAgency'], xiniuLP['institutionId']))