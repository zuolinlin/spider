from scrapy.cmdline import execute


def crawl(spiders):
    for spider in spiders:
        execute(['scrapy', 'crawl', spider])


if __name__ == '__main__':

    crawl([
        'zdb'  # 投资人物
    ])

