# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time

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
    """
        IT桔子-公司数据
    """

    def process_item(self, item, spider):
        logger.log("===> " + str(item))
        # insert("INSERT INTO `xsbbiz`.`itjuzi_company` (`company_name`, `company_logo`) "
        #        "VALUES (%s, %s)",
        #        (item['company_name'], item['company_logo']))


class ZhiPinSpiderPipeline(object):
    """
    Boss直聘-招聘数据
    """

    def process_item(self, item, spider):
        # logger.log("===> " + str(item))
        if item['link'] is not None:
            job = spider.fetchone(
                "SELECT 1 FROM `xsbbiz`.`zhipin_recruitment` WHERE `link`='%s'" % (
                    item['link'])
            )
        else:
            return
        if job is None:
            spider.insert(
                "INSERT INTO `xsbbiz`.`zhipin_recruitment` (`company_name`, `job_name`, `location`, `education`, `years`, `salary`, `release_time`,  `platform`, `link`, `update_time`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item['company_name'], item['job_name'], item['location'], item['education'], item['years'],
                 item['salary'], item['release_time'], item['platform'], item['link'], time.localtime()))
        else:
            spider.insert(
                """
                UPDATE
                      `xsbbiz`.`zhipin_recruitment`
                    SET
                      `company_name` = %s,
                       `job_name` = %s,
                      `location` = %s,
                      `education` = %s,
                      `years` = %s,
                      `salary` = %s,
                      `release_time` = %s,
                      `platform` = %s,
                      `update_time` = %s
                    WHERE `link` = %s
                """, (
                    item['company_name'],
                    item['job_name'],
                    item['location'],
                    item['education'],
                    item['years'],
                    item['salary'],
                    item['release_time'],
                    item['platform'],
                    time.localtime(),
                    item['link']
                )
            )


class ZhiLianSpiderPipeline(object):
    """
    智联招聘-招聘数据
    """

    def process_item(self, item, spider):
        # logger.log("===> " + str(item))
        if item['link'] is not None:
            job = spider.fetchone("SELECT 1 FROM `xsbbiz`.`zhilian_recruitment` WHERE `link`='%s'" % (item['link']))
        else:
            return
        if job is None:  # 不存在
            spider.insert(
                "INSERT INTO `xsbbiz`.`zhilian_recruitment` (`company_name`, `job_name`, `location`, `education`, `years`, `salary`, `release_time`,  `platform`, `link`, `update_time`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item['company_name'], item['job_name'], item['location'], item['education'], item['years'],
                 item['salary'], item['release_time'], item['platform'], item['link'], time.localtime()))
        else:
            spider.insert(
                """
                UPDATE
                      `xsbbiz`.`zhilian_recruitment`
                    SET
                      `company_name` = %s,
                      `job_name` = %s,
                      `location` = %s,
                      `education` = %s,
                      `years` = %s,
                      `salary` = %s,
                      `release_time` = %s,
                      `platform` = %s,
                      `update_time` = %s
                    WHERE `link` = %s
                """, (
                    item['company_name'],
                    item['job_name'],
                    item['location'],
                    item['education'],
                    item['years'],
                    item['salary'],
                    item['release_time'],
                    item['platform'],
                    time.localtime(),
                    item['link']
                )
            )


class BaiduZhaopinSpiderPipeline(object):
    """
    百度招聘-招聘数据
    """

    def process_item(self, item, spider):
        # logger.log("===> " + str(item))
        if item['company_name'] is not None & item['job_name'] is not None & item['platform'] is not None:
            job = spider.fetchone(
                "SELECT 1 FROM `xsbbiz`.`baidu_recruitment` WHERE `company_name`='%s' AND `job_name`='%s' AND `platform`='%s'" % (
                    item['company_name'], item['job_name'], item['platform'])
            )
        else:
            return
        if job is None:
            spider.insert(
                "INSERT INTO `xsbbiz`.`baidu_recruitment` (`company_name`, `job_name`, `location`, `education`, `years`, `salary`, `release_time`,  `platform`, `update_time`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (item['company_name'], item['job_name'], item['location'], item['education'], item['years'],
                 item['salary'], item['release_time'], item['platform'], time.localtime()))
        else:
            spider.insert(
                """
                UPDATE
                      `xsbbiz`.`baidu_recruitment`
                    SET
                      `location` = %s,
                      `education` = %s,
                      `years` = %s,
                      `salary` = %s,
                      `release_time` = %s,
                      `update_time` = %s
                    WHERE `company_name` = %s AND `job_name` = %s AND `platform` = %s
                """, (
                    item['location'],
                    item['education'],
                    item['years'],
                    item['salary'],
                    item['release_time'],
                    time.localtime(),
                    item['company_name'],
                    item['job_name'],
                    item['platform']
                )
            )
