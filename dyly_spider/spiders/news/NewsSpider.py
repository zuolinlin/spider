# -*- coding: utf-8 -*-
import time
import uuid

from dyly_spider.spiders.BaseSpider import BaseSpider


class NewsSpider(BaseSpider):

    def __init__(self, *a, **kw):
        super(NewsSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass

    def insert_new(self, out_id, push_date, title, new_type, source, content, spider_source):
        """
        添加数据
        :param out_id: 外部编号
        :param push_date: 时间
        :param title: 标题
        :param new_type: 新闻类型
        :param source: 来源
        :param content: 内容
        :param spider_source: 爬取来源
        :return: 最后一行编号
        """
        return self.insert("""
                        INSERT INTO `spider_news` (
                          `new_id`,
                          `out_id`,
                          `push_date`,
                          `title`,
                          `new_type`,
                          `source`,
                          `content`,
                          `spider_source`,
                          `modify_date`
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(uuid.uuid4()).replace("-", ""),
                            out_id,
                            push_date,
                            title,
                            new_type,
                            source,
                            content,
                            spider_source,
                            time.localtime()
                        ))


