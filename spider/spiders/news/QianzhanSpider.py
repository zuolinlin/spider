
from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider


class QianzhanSpider(NewsSpider):
    name = "qianzhan_news"
    allowed_domains = ["qianzhan.com"]



    def start_requests(self):
        url = 'https://www.qianzhan.com/analyst/'
        yield Request(
            url = url,
            dont_filter=True
        )

    def __init__(self, *a, **kw):
        super(QianzhanSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def parse(self, response):
        data_list = response.xpath('//*[@id="divLatest"]/li')
        # print(data_list)
        for data in data_list:

            title =data.xpath('./div[@class="ml220"]/p/a/text()').extract_first()


            tim = data.xpath('./div[@class="ml220"]/div/p/span/span/text()').extract_first()
            push_time = str(tim).split("• ")[1]

            digest = data.xpath('./div[@class="ml220"]/p/text()').extract_first()

            url = data.xpath('./div/p[1]/a/@href').get().strip()
            detail_url = 'https:' + str(url)

            yield Request(
               detail_url,
               meta={"title": title,
                   "push_time": push_time,
                     "digest": digest
                     },
               callback = self.detail
             )

    def detail(self, response):
        title = response.meta['title']
        push_time = response.meta['push_time']
        response.url
        # 外部编号
        url = response.url
        splits = str(url).split('/')

        out_id = splits[-1][:-5]
        # new_type = response.meta['new_type']
        new_type = "问答"

        # 来源
        source = "前瞻网"

        # 摘要
        digest = response.meta['digest']

        # 内容
        content = response.xpath('/html/body').extract_first()

        # 爬取来源
        spider_source = 95

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     # content,
        #     response.url,
        #     spider_source
        # )

        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            response.url,
            spider_source
        )


