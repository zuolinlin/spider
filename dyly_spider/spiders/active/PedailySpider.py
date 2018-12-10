import scrapy

from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
from scrapy import Request

"""
投资界-清科集团   == 
"""


class PedailySpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "pedaily_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["pedaily.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://news.pedaily.cn/events/{event_type}/{pageNo}'
    active_types = [
        {"name": "地方论坛", "value": "events-e3"},
        {"name": "Venture50", "value": "events-e9"},
        {"name": "股权投资论坛", "value": "events-e1"}

    ]

    def __init__(self, *a, **kw):
        super(PedailySpider, self).__init__(*a, **kw)

    def start_requests(self):
        for active_type in self.active_types:
            yield Request(
                self.start_urls.format(event_type=active_type.get("value"), pageNo=1),
                meta=active_type,
                dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//ul[@class="news-list"]/li')
        if data_list is not None:
            for data in data_list:
                title = data.xpath('./div[@class="txt"]/h3/a/text()').extract_first()
                link = data.xpath('./div[@class="txt"]/h3/a/@href').extract_first()
                times = data.xpath('./div[@class="txt"]/div[@class="info"]/text()[1]').extract_first()
                times = str(times)[3:14]
                times = str(times).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                place = data.xpath('./div[@class="txt"]/div[@class="info"]/text()[2]').extract_first()
                strs = str(place).split('-')
                place = strs[len(strs) -1]
                source = "投资界-清科集团"
                classify = response.meta['name']
                self.insert_new(
                    title,
                    times,
                    place,
                    None,
                    classify,
                    link,
                    source
                )
        next_url = response.xpath('//div[@class="page-list page"]/a[@class="next"]/@href').extract_first()
        if next_url is not None:
            yield Request(
                next_url,
                meta=response.meta,
                dont_filter=True,
                callback=self.parse
            )
