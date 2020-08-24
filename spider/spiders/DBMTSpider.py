# -*- coding: utf-8 -*-
import time
import uuid

from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.selector import SelectorList

from spider.spiders.BaseSpider import BaseSpider

exclude_tags = ['img', 'video', 'audio', 'object', 'embed']


class DBMTSpider(BaseSpider):

    name = None

    def __init__(self, *a, **kw):
        super(DBMTSpider, self).__init__(*a, **kw)

    def parse(self, response):
        pass
    def select_spider_store_by_store_out_id(self ,out_id):
        return self.fetchone(
            "SELECT * FROM `spider_store` WHERE `out_id`='%s'" % (out_id)
        )
    def insert_spider_store(self, out_id, settle_code, store_code, store_name, mobile, order_num, longitude, latitude, store_addr,specific_addr,company_name,brand_id,brand_name,logo,tel,star,business_start_time,business_end_time,state,verify_state,is_delete):
        """
        添加数据
        :param out_id: 外部编号
        :param settle_code: 时间
        :param store_code: 标题
        :param store_name: 新闻类型
        :param order_num: 来源
        :param longitude: 摘要
        :param latitude: 内容(html字符串/Selector)
        :param store_addr: 来源地址
        :param specific_addr: 爬取来源
        :param company_name: 时间
        :param brand_id: 标题
        :param brand_name: 新闻类型
        :param logo: 来源
        :param tel: 摘要
        :param star: 内容(html字符串/Selector)
        :param business_start_time: 来源地址
        :param business_end_time: 爬取来源
        :param state: 内容(html字符串/Selector)
        :param verify_state: 来源地址
        :param is_delete: 爬取来源
        :return: 最后一行编号
        """
        if out_id is not None :
            pojo = self.fetchone(
                "SELECT 1 FROM `spider_store` WHERE `out_id`='%s' " % (out_id)
            )
        else:
            return
        if pojo is None:

            return self.insert("""
                            INSERT INTO `spider_store` (
                              `out_id`,
                              `settle_code`,
                              `store_code`,
                              `store_name`,
                              `mobile`,
                              `order_num`,
                              `longitude`,
                              `latitude`,
                              `store_addr`,
                              `specific_addr`,
                              `company_name`,
                              `brand_id`,
                              `brand_name`,
                              `logo`,
                              `tel`,
                              `star`,
                              `business_start_time`,
                              `business_end_time`,
                              `state`,
                              `verify_state`,
                              `is_delete`
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                out_id,
                                settle_code,
                                store_code,
                                store_name,
                                mobile,
                                order_num,
                                longitude,
                                latitude,
                                store_addr,
                                specific_addr,
                                company_name,
                                brand_id,
                                brand_name,
                                logo,
                                tel,
                                star,
                                business_start_time,
                                business_end_time,
                                state,
                                verify_state,
                                is_delete
                            ))
    def select_spider_settle_by_store_out_id(self ,out_id):

        return self.fetchone(
            "SELECT * FROM `spider_settle` WHERE `out_id`='%s'" % (out_id)
        )

    def insert_spider_settle(self, out_id, settle_code, company_name, company_addr, mobile, verify_state, is_delete):
        """
        添加数据
        :param out_id: 外部编号
        :param settle_code: 公司或者个人标识
        :param company_name: 公司名称
        :param company_addr: 公司地址
        :param mobile: 联系方式
        :param business_start_time: 营业开始时间
        :param business_end_time: 营业结束时间
        :param verify_state: 审核状态 0:待审核 1：待完善 2：正常 3：已禁用'
        :param is_delete: 状态: 0.未删除 1已删除
        """
        if out_id is not None :
            pojo = self.fetchone(
                "SELECT * FROM `spider_settle` WHERE `out_id`='%s'" % (out_id)
            )
        else:
            return
        if pojo is None:
            return self.insert("""
                              INSERT INTO `spider_settle` (
                                `out_id`,
                                `settle_code`,
                                `company_name`,
                                `company_addr`,
                                `mobile`,
                            
                                `verify_state`,
                                `is_delete`
                              ) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)
                              """, (
                out_id,
                settle_code,
                company_name,
                company_addr,
                mobile,
                verify_state,
                is_delete
            ))
        else:
            return pojo

    def insert_spider_project(self, out_id, project_out_id,settle_code, name, sub_title, original_price, last_price, sale_num, server_id, icon,state,del_state):
        """
        添加数据
        :param out_id: 外部编号
        :param settle_code: 时间
        :param name: 标题
        :param sub_title: 新闻类型
        :param original_price: 来源
        :param sale_num: 摘要
        :param icon: 内容(html字符串/Selector)
        :param state: 来源地址
        :param del_state: 爬取来源
        :return: 最后一行编号
        """

        return self.insert("""
                        INSERT INTO `spider_project` (
                          `out_id`,
                          `project_out_id`,
                          `settle_code`,
                          `name`,
                          `sub_title`,
                          `original_price`,
                          `last_price`,
                          `sale_num`,
                          `server_id`,
                          `icon`,
                          `state`
                        ) 
                        VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            out_id,
                            project_out_id,
                            settle_code,
                            name,
                            sub_title,
                            original_price,
                            last_price,
                            sale_num,
                            server_id,
                            icon,
                            state
                        ))


    def select_spider_project_by_store_out_id_project_out_id(self, out_id, project_out_id):
        """
        添加数据
        :param out_id: 外部编号
        :param project_out_id:
        """
        return self.fetchone(
            "SELECT * FROM `spider_project` WHERE `out_id`='%s' AND `project_out_id`=%s " % (out_id,project_out_id)
        )
    def select_spider_store_project_by_store_out_id_project_out_id(self,out_id, project_out_id):
        return self.fetchone(
            "SELECT * FROM `spider_store_project` WHERE `out_id`='%s' AND `project_out_id`=%s " % (out_id,project_out_id)
        )
    def insert_spider_store_project(self, store_code, project_id,out_id, project_out_id):
        """
        添加数据
        :param store_code: 外部编号
        :param project_id: 时间
        """

        return self.insert("""
                        INSERT INTO `spider_store_project` (
                          `store_code`,
                          `project_id`,
                          `out_id`,
                          `project_out_id`
                          
                        ) 
                        VALUES (%s, %s,%s, %s)
                        """, (
                            store_code,
                            project_id,
                            out_id,
                            project_out_id
                        ))

    def select_spider_project_detail_by_project_out_id(self, project_out_id):
        """
        添加数据
        :param project_out_id:
        """
        return self.fetchone(
            "SELECT * FROM `spider_project_detail` WHERE `project_out_id`=%s " % (project_out_id)
        )

    def insert_spider_project_detail(self, project_out_id, project_id, imgUrls):
        """
        添加数据
        :param store_code: 外部编号
        :param project_id: 时间
        """

        return self.insert("""
                        INSERT INTO `spider_project_detail` (
                          `project_out_id`,
                          `project_id`,
                          `image_url`

                        ) 
                        VALUES (%s, %s,%s)
                        """, (
            project_out_id,
            project_id,
            imgUrls
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
