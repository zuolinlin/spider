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

