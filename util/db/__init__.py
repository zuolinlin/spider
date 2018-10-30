# -*- coding: utf-8 -*-
import pymysql
from util import cy_logger


class DBMysql:

    def get_connection(self):
        # 打开数据库连接
        return pymysql.connect(host='rdsb3v4p9d76w56130cbo.mysql.rds.aliyuncs.com', port=3306,
                               user='admin_dyly',
                               passwd='admin_dyly', db='xsbbiz', charset='utf8')

    def execute(self, sql, params):
        # 使用cursor()方法获取操作游标
        connection = self.get_connection()
        # cursor = connection.cursor()

        try:
            # 执行sql语句
            # cursor.execute(sql)
            # cursor.executemany("insert into tb7(user,pass,licnese)values(%s,%s,%s)",
            # [("u1","u1pass","11111"),("u2","u2pass","22222")])
            with connection.cursor() as cursor:
                # 执行sql语句
                if type(params) == list:
                    cursor.executemany(sql, params)
                else:
                    cursor.execute(sql, params)
                # 获取自增id
                pk = connection.insert_id()
                connection.commit()
            if pk:
                cy_logger.log("执行成功！返回最后一条主键为==> " + str(pk))
            else:
                cy_logger.log("执行成功")
            return pk
        except Exception as e:
            cy_logger.error(str(e))
            # 发生错误时回滚
            connection.rollback()
        finally:
            # 关闭数据库连接
            connection.close()

    def fetchall(self, sql):
        # 使用cursor()方法获取操作游标
        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            return cursor.fetchall()
        except Exception as e:
            cy_logger.error(e)
        finally:
            # 关闭数据库连接
            connection.close()

    def fetchone(self, sql):
        # 使用cursor()方法获取操作游标
        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            return cursor.fetchone()
        except Exception as e:
            cy_logger.error(e)
        finally:
            # 关闭数据库连接
            connection.close()


mysql = DBMysql()
