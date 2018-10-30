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


class ItjuziItem(scrapy.Item):
    # define the fields for your item here like:
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
