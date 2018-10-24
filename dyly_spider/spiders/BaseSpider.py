# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request

from util.db import mysql


class BaseSpider(scrapy.Spider):

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

