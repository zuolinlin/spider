# -*- coding: utf-8 -*-
from scrapy.cmdline import execute


def crawl(spiders):
    for spider in spiders:
        execute(['scrapy', 'crawl', spider])


if __name__ == '__main__':
    crawl([
        # 'zdb_selenium',  # 投资人物(需要谷歌浏览器渲染 版本>= 65.0.3325.0)
        # 'xiniu',  # 投资人物
        'hdj',  # 活动行页面数据
    ])
