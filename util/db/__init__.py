# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB
from util import cy_logger

POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示没有限制
    mincached=2,  # 初始化时，连接池至少创建的空闲的连接，0表示不创建
    maxcached=5,  # 连接池空闲的最多连接数，0和None表示没有限制
    maxshared=3,  # 连接池中最多共享的连接数量，0和None表示全部共享
    blocking=True,  # 链接池中如果没有可用共享连接后，是否阻塞等待，True表示等待，False表示不等待然后报错
    setsession=[],  # 开始会话前执行的命令列表
    ping=0,  # ping Mysql 服务端，检查服务是否可用
    host='rdsb3v4p9d76w56130cbo.mysql.rds.aliyuncs.com',
    port=3306,
    user='admin_dyly',
    password='admin_dyly',
    database='xsbbiz',
    charset='utf8'
)


class DBMysql:

    def get_connection(self):
        # 获取数据库连接
        return POOL.connection()
        # 打开数据库连接
        # return pymysql.connect(host='rdsb3v4p9d76w56130cbo.mysql.rds.aliyuncs.com', port=3306,
        #                        user='admin_dyly',
        #                        passwd='admin_dyly', db='xsbbiz', charset='utf8')

    def execute(self, sql, params):
        if type(params) == list and len(params) == 0:
            return
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
                pk = cursor.lastrowid
                connection.commit()
            if pk:
                cy_logger.log("executes successfully! last_row_id==> " + str(pk))
            else:
                cy_logger.log("executes successfully")
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

    def select_rows_paper(self, sql, param=None, page_no=1, page_size=20):
        """
        分页查询
        """
        # total = self.select_row_count(sql, param)  # 总记录数
        offset = (page_no - 1) * page_size  # 偏移量
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if param:
                    sql = sql + '%s' % param

                cursor.execute("SELECT COUNT(1) FROM (%s) tmp" % sql)
                total = cursor.fetchall()[0][0]

                sql = sql + ' LIMIT %s, %s' % (offset, page_size)
                cy_logger.log(sql)
                cursor.execute(sql)
                rows = cursor.fetchall()

                # 总页数
                pages = int(total / page_size) if total % page_size == 0 else int(total / page_size) + 1
                return {'total': total, 'page_no': page_no, 'pages': pages, 'rows': rows}
        except Exception as e:
            cy_logger.error(e)
        finally:
            connection.close()


mysql = DBMysql()
