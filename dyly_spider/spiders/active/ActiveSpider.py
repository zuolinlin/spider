# -*- coding: utf-8 -*-
import time
import uuid

from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.selector import SelectorList

from dyly_spider.spiders.BaseSpider import BaseSpider


class ActiveSpider(BaseSpider):
    name = None

    def __init__(self, *a, **kw):
        super(ActiveSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass

    def insert_new(self,  title, times, place, tag, classify, link, source):
        """
        添加数据
        :param title: 标题
        :param time: 活动时间
        :param place: 活动地点
        :param tag: 标签
        :param classify: 分类
        :param link: 来源地址（详情地址）
        :param source: 爬取来源
        :return: 最后一行编号
        """
        if link is not None and source is not None:
            pojo = self.fetchone(
                "SELECT 1 FROM `financial_activities` WHERE `link`='%s' AND `source`='%s' " % (
                    link, source)
            )
        else:
            return
        if pojo is None:
            self.insert("""
                                                                     INSERT INTO `financial_activities` (
                                                                       `id`,
                                                                       `title`,
                                                                       `time`,
                                                                       `place`,
                                                                       `tag`,
                                                                       `classify`,
                                                                       `link`,
                                                                       `source`,
                                                                       `createTime`

                                                                     ) 
                                                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                                                     """, (
                                                                        str(uuid.uuid4()).replace("-", ""),
                                                                        title,
                                                                        times,
                                                                        place,
                                                                        tag,
                                                                        classify,
                                                                        link,
                                                                        source,
                                                                        time.localtime()
                                                                     ))
