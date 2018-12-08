import scrapy

from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
from scrapy import Request


class LjzforumSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "ljzforum_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["ljzforum.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.ljzforum.com/activity/query.do?'

    def __init__(self, *a, **kw):
        super(LjzforumSpider, self).__init__(*a, **kw)

    def start_requests(self):
        scrapy.FormRequest(
            url=self.start_urls,
            formdata={
                      "limitStart": "0",
                      "limitEnd": "21"},

            callback=self.parse
        )

    def parse(self, response):
        print(response)
        pass
