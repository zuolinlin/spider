# -*- coding: utf-8 -*-
import json
import time
import uuid

from scrapy import Request

from dyly_spider.spiders.BaseSpider import BaseSpider


class NewsSpider(BaseSpider):

    def __init__(self, *a, **kw):
        super(NewsSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass

    def insert_new(self, push_date, title, new_type, source, content, spider_source):
        self.insert("""
        INSERT INTO `spider_news` (
          `new_id`,
          `push_date`,
          `title`,
          `new_type`,
          `source`,
          `content`,
          `spider_source`,
          `modify_date`
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()).replace("-", ""),
            push_date,
            title,
            new_type,
            source,
            content,
            spider_source,
            time.localtime()
        ))


