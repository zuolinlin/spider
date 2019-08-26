
from scrapy import Request

from dyly_spider.spiders.news.NewsSpider import NewsSpider


class QianzhanSpider(NewsSpider):
    name = "qianzhan_news"
    allowed_domains = ["qianzhan.com"]



    def start_requests(self):
        url = 'https://www.qianzhan.com/analyst/'
        yield Request(
            url=url,
            dont_filter=True
        )

    def __init__(self, *a, **kw):
        super(QianzhanSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = response.xpath('//*[@id="divLatest"]')
        for data in data_list:
            title =data.xpath('./li/div/p/text()').extract_first()
            tim = data.xpath('//*[@id="divLatest"]/li[1]/div/div/p/span/span/text()').extract_first()
            tt = str(tim).split("• ")[1]
            url = data.xpath('//*[@id="divLatest"]/li[1]/div/p[1]/a/@href').get().strip()
            detailurl = str(url)[2:]
            yield Request(
               detailurl,
               meta={"title": title,
                   "tt": tt},
               callback=self.detail
             )

    def detail(self, response):
        title =response['title']
        push_time = response['tt']
        response.url
        # 外部编号
        url = response.url
        splits = str(url).split('/')
        out_id = splits[4] + splits[5]

        new_type = response.meta['new_type']
        # 来源
        source = "前瞻网"
        # 内容
        content = response.xpath('/html/body').extract_first()
        # 爬取来源
        spider_source = 95
        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            None,
            content,
            response.url,
            spider_source
        )


