# -*- coding: utf-8 -*-
import logging

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
        return self.db.execute(sql, params)

    def exec_sql(self, sql, params):
        self.db.execute(sql, params)

    def fetchone(self, sql):
        return self.db.fetchone(sql)

    def fetchall(self, sql):
        return self.db.fetchall(sql)

    def select_rows_paper(self, sql, param=None, page_no=1, page_size=20):
        return self.db.select_rows_paper(sql, param, page_no, page_size)

    def log_error(self, msg):
        self.log(msg, logging.ERROR)

