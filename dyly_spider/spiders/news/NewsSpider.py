# -*- coding: utf-8 -*-
import time
import uuid

from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.selector import SelectorList

from dyly_spider.spiders.BaseSpider import BaseSpider

exclude_tags = ['img', 'video', 'audio', 'object', 'embed']


class NewsSpider(BaseSpider):

    name = None

    def __init__(self, *a, **kw):
        super(NewsSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass

    def insert_new(self, out_id, push_date, title, new_type, source, digest, content, source_url, spider_source):
        """
        添加数据
        :param out_id: 外部编号
        :param push_date: 时间
        :param title: 标题
        :param new_type: 新闻类型
        :param source: 来源
        :param digest: 摘要
        :param content: 内容(html字符串/Selector)
        :param source_url: 来源地址
        :param spider_source: 爬取来源
        :return: 最后一行编号
        """
        if out_id is not None and spider_source is not None:
            pojo = self.fetchone(
                "SELECT 1 FROM `spider_news` WHERE `out_id`='%s' AND `spider_source`=%s" % (out_id, spider_source)
            )
        else:
            return
        if pojo is None:
            #content = remove_image_voide_audio(content)
            return self.insert("""
                            INSERT INTO `spider_news` (
                              `new_id`,
                              `out_id`,
                              `push_date`,
                              `title`,
                              `new_type`,
                              `source`,
                              `digest`,
                              `content`,
                              `source_url`,
                              `spider_source`,
                              `modify_date`
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                str(uuid.uuid4()).replace("-", ""),
                                out_id,
                                push_date,
                                title,
                                new_type,
                                source,
                                digest,
                                content,
                                source_url,
                                spider_source,
                                time.localtime()
                            ))

    def insert_new_1(self, out_id, push_date, title, new_type, source, digest, content, source_url, spider_source, coverimage_url):
        """
        添加数据
        :param out_id: 外部编号
        :param push_date: 时间
        :param title: 标题
        :param new_type: 新闻类型
        :param source: 来源
        :param digest: 摘要
        :param content: 内容(html字符串/Selector)
        :param source_url: 来源地址
        :param spider_source: 爬取来源
        :param coverimage_url: 封面图
        :return: 最后一行编号
        """
        if out_id is not None and spider_source is not None:
            pojo = self.fetchone(
                "SELECT 1 FROM `spider_news` WHERE `out_id`='%s' AND `spider_source`=%s" % (out_id, spider_source)
            )
        else:
            return
        if pojo is None:
            #content = remove_image_voide_audio(content)
            return self.insert("""
                            INSERT INTO `spider_news` (
                              `new_id`,
                              `out_id`,
                              `push_date`,
                              `title`,
                              `new_type`,
                              `source`,
                              `digest`,
                              `content`,
                              `source_url`,
                              `spider_source`,
                              `modify_date`,
                              coverimage_url
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                str(uuid.uuid4()).replace("-", ""),
                                out_id,
                                push_date,
                                title,
                                new_type,
                                source,
                                digest,
                                content,
                                source_url,
                                spider_source,
                                time.localtime(),
                                coverimage_url
                            ))

def remove_image_voide_audio(content):
    if content is None:
        return None
    if type(content) == Selector:
        content = content.get()
    if type(content) == SelectorList:
        content = "".join(content.getall())
    if len(content) > 0:
        soup = BeautifulSoup(content, "lxml")
        [s.extract() for s in soup(exclude_tags)]
        return str(soup.body)[6:-7]
