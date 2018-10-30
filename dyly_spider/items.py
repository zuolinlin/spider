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
    name = scrapy.Field()       # 姓名
    company = scrapy.Field()    # 公司


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
