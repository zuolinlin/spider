import re
import json

from scrapy import Request, signals
from util.XPathUtil import str_to_selector
from spider.spiders.news.NewsSpider import NewsSpider



"""
速途网 == 电商、o2o、游戏、it、物联网、智能硬件、移动互联网
"""


class SootooSpider(NewsSpider):
    name = "sootoo_news"
    allowed_domains = ["sootoo.com"]
    #  开始爬取的地址  按照行业分类来爬取

    base_url = "http://www.sootoo.com/tag/{name}"
    news_types = [
        {"name": "news", "value": "资讯"},
        {"name": "unicorn", "value": "独角兽"},
        {"name": "5", "value": "互联网"},
        {"name": "ct", "value": "创投"},
        {"name": "18", "value": "游戏"},
        {"name": "22", "value": "财经"}
    ]

    def __init__(self, *a, **kw):
        super(SootooSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def start_requests(self):
        for news_type in self.news_types:
            yield Request(
                self.base_url.format(name=news_type.get("name")),
                meta=news_type,
                dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath("//ul[contains(@class, 'article-list')]/li")
        # print(data_list)
        if data_list is not None:
            for data in data_list:
                detail_url = data.xpath('./div[@class="item-content"]//h2/a/@href').extract_first()

                out_id = re.findall(r'content/(.*?).shtml', detail_url)[0]
                title = data.xpath('./div[@class="item-content"]/h2/a/text()').extract_first()

                # print(out_id, detail_url, title)

                response.meta.update(
                    {
                        "out_id": out_id,
                        "title":title
                    }
                )

                yield Request(
                    detail_url,
                    meta=response.meta,
                    callback=self.detail
                )

        # # 获取下一页的数据
        # pages = 10
        # while self.current_page < pages:
        #     self.current_page += 1
        #     next_url = response.url + '/page/' + str(self.current_page)
        #
        #     yield Request(
        #         next_url, callback=self.parse
        #     )


    def detail(self, response):
        out_id = response.meta['out_id']
        push_time = response.xpath("//div[contains(@class, 'entry-info')]/span[2]/text()").extract_first()
        if push_time.find('年') == -1:
            push_time = response.xpath("//div[contains(@class, 'entry-info')]/span[4]/text()").extract_first()
        push_time = push_time.replace('年','-' ).replace('月','-').replace('日',' ') + ':00'

        title = response.meta['title']
        news_type = response.meta['value']
        source = '速途网'
        digest = None
        content = response.xpath("/html/body").extract_first()
        source_url = response.url
        spider_source = 60

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     news_type,
        #     source,
        #     digest,
        #     # content,
        #     source_url,
        #     spider_source
        # )

        self.insert_new(
            out_id,
            push_time,
            title,
            news_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )