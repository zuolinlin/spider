# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from util import cy_logger as logger
from util.db import mysql


def insert(sql, params):
    mysql.execute(sql, params)


def exec_sql(sql, params):
    mysql.execute(sql, params)


class DylySpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ZdbSpiderPipeline(object):
    """
    投资界-投资人物
    """

    def process_item(self, item, spider):
        logger.log("*" * 100)
        logger.log("===> " + str(item))
        logger.log("*" * 100)
        insert("INSERT INTO `xsbbiz`.`spider_test` (`name`, `company`) "
               "VALUES (%s, %s)",
               (item['name'], item['company']))


class ItjuziSpiderPipeline(object):
    def process_item(self, item, spider):
        logger.log("===> " + item["company_name"])
