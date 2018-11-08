# -*- coding: utf-8 -*-
import logging


# 自定义的日志输出
def log(msg, level=logging.INFO):
    logging.log(level, msg)
    # if level == logging.WARNING:
    #     for line in traceback.format_stack():
    #         logging.log(level, "警告信息===>" + line.strip())
    # elif level == logging.ERROR:
    #     for line in traceback.format_stack():
    #         logging.log(level, "错误信息===>" + line.strip())


def error(msg):
    log(msg, logging.ERROR)


def debug(msg):
    log(msg, logging.DEBUG)

