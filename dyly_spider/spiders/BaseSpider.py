# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider
from util.db import mysql


class BaseSpider(CrawlSpider):

    name = "base"

    def __init__(self, *a, **kw):
        super(BaseSpider, self).__init__(*a, **kw)
        self.db = mysql

    def parse(self, response):
        pass

    def insert(self, sql, params):
        self.db.execute(sql, params)

    def exec_sql(self, sql, params):
        self.db.execute(sql, params)

    def fetchone(self, sql):
        return self.db.fetchone(sql)

