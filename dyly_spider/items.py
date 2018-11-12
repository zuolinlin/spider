# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DylySpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ZdbItem(scrapy.Item):
    """
    投资界-投资人物
    """
    name = scrapy.Field()  # 姓名
    company = scrapy.Field()  # 公司


class XiniuInstitutionItem(scrapy.Item):
    """
    机构信息
    """
    logo = scrapy.Field()  # logo
    name = scrapy.Field()  # 机构名称
    establishmentTime = scrapy.Field()  # 成立时间
    describe = scrapy.Field()  # 机构描述


class XiniuInvestmentEvents(scrapy.Item):
    """
    烯牛投资事件
    """
    investmentTime = scrapy.Field()  # 投资时间
    companyName = scrapy.Field()  # 公司名称
    companyLogo = scrapy.Field()  # 公司logo
    companyDescribe = scrapy.Field()  # 公司描述
    industry = scrapy.Field()  # 行业
    area = scrapy.Field()  # 地区
    currentTurn = scrapy.Field()  # 投资轮次
    amount = scrapy.Field()  # 投资金额
    investors = scrapy.Field()  # 投资方
    institutionId = scrapy.Field()  # 机构id


class ItjuziCompanyItem(scrapy.Item):
    """
    IT桔子-公司数据
    """
    # 公司名字
    company_name = scrapy.Field()
    # logo地址
    company_logo = scrapy.Field()
    # 公司id
    company_id = scrapy.Field()
    # 公司地址
    company_addr = scrapy.Field()
    # 公司描述
    company_des = scrapy.Field()
    # 公司行业
    company_fa = scrapy.Field()
    # 公司子行业
    company_son = scrapy.Field()
    # 公司最新融资情况
    company_recent = scrapy.Field()
    # 公司资产总额
    company_count = scrapy.Field()
    # 公司估价
    company_money = scrapy.Field()
    # 公司全名
    company_fullname = scrapy.Field()
    # 公司成立时间
    company_btime = scrapy.Field()
    # 公司规模
    company_people = scrapy.Field()
    # 公司营运情况
    company_operate = scrapy.Field()
    # 团队人员姓名
    perosonname = scrapy.Field()
    # 职位
    perosonposition = scrapy.Field()
    # 个人简介
    perosondes = scrapy.Field()
    # 公司产品
    product = scrapy.Field()
    # 公司标语
    company_slogan = scrapy.Field()


class XiniuInstitudynamic(scrapy.Item):
    """
    烯牛抓去机构动态列表数据
    """
    dynamicTime = scrapy.Field()  # 动态时间
    dynamicType = scrapy.Field()  # 动态类型
    content = scrapy.Field()  # 内容
    keyWord = scrapy.Field()  # 关键字
    institutionId = scrapy.Field()  # 关联机构id


class XiniuNews(scrapy.Item):
    """
    烯牛抓去机构新闻数据
    """
    newsTime = scrapy.Field()  # 新闻时间
    source1 = scrapy.Field()  # 新闻来源1
    source2 = scrapy.Field()  # 新闻来源2
    title = scrapy.Field()  # 新闻标题
    url = scrapy.Field()  # 地址
    institutionId = scrapy.Field()  # 关联机构id


class XiniuFun(scrapy.Item):
    """
    烯牛投资机构基金列表
    """
    recordTime = scrapy.Field()  # 备案时间
    fundName = scrapy.Field()  # 基金名称
    url = scrapy.Field()  # url
    registeredCapita = scrapy.Field()  # 注册资本
    partner = scrapy.Field()  # 执行事务合伙人
    foundingTime = scrapy.Field()  # 工商成立时间
    institutionId = scrapy.Field()  # 关联机构id


class XiniuFundmanager(scrapy.Item):
    """
    烯牛基金管理人列表
    """
    foundingTime = scrapy.Field()  # 成立时间
    name = scrapy.Field()  # 名称
    legalRepresentative = scrapy.Field()  # 法人代表
    managementFund = scrapy.Field()  # 管理基金
    recordTime = scrapy.Field()  # 基金备案时间
    institutionId = scrapy.Field()  # 关联机构id


class XiniuLP(scrapy.Item):
    """
    烯牛LP数据
    """
    lpName = scrapy.Field()  # Lp名称
    ownershipOrganization = scrapy.Field()  # 归属机构
    fundsNum = scrapy.Field()  # 参与基金数
    cooperationAgency = scrapy.Field()  # 其它合作机构
    institutionId = scrapy.Field()  # 关联机构Id


class XiniuCompany(scrapy.Item):
    """
     烯牛公司数据
    """
    id = scrapy.Field()  # 公司Id
    logoUrl = scrapy.Field()  # 公司logo
    companyFullName = scrapy.Field()  # 公司全称
    companyAbbreviation = scrapy.Field()  # 公司简称
    telephone = scrapy.Field()  # 联系电话
    email = scrapy.Field()  # email 邮箱
    website = scrapy.Field()  # 网站
    foundingTime = scrapy.Field()  # 成立时间
    city = scrapy.Field()  # 城市
    inaword = scrapy.Field()  # 一句话介绍
    advantage = scrapy.Field()  # 公司优势
    industryClassification = scrapy.Field()  # 行业分类
    legalRepresentative = scrapy.Field()  # 法人代表
    description = scrapy.Field()  # 描述
    url = scrapy.Field()  # 进入烯牛详情页的url(为抓取详情页的数据临时存放)


class ZhipinItem(scrapy.Item):
    """
    Boss直聘职位数据
    """
    company_name = scrapy.Field()  # 公司
    job_name = scrapy.Field()  # 职位
    location = scrapy.Field()  # 地区
    education = scrapy.Field()  # 学历
    years = scrapy.Field()  # 年限
    salary = scrapy.Field()  # 薪资
    field = scrapy.Field()  # 领域
    release_time = scrapy.Field()  # 发布时间
    platform = scrapy.Field()  # 发布平台
