from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json

"""
  量子位
"""
class QbitaiSpider(NewsSpider):
    start_urls = ["https://www.qbitai.com/page/{n}".format(n=n) for n in range(1, 2)]
    name = "qbitai_news"
    allowed_domains = ["qbitai.com"]

    def start_requests(self):
        # url = "https://www.qbitai.com/page/1"

        for url in self.start_urls:
            yield Request(
                url,
                callback=self.parse
            )

    def __init__(self, *a, **kw):
        super(QbitaiSpider, self).__init__(*a, **kw)
        self.current_page = 1

    def parse(self, response):
        data_list = response.xpath('//div[@class="article_list"]/div[@class="picture_text"]')
        for data in data_list:
            detail_url =data.xpath('./div[@class="picture"]/a/@href').extract_first()
            title = data.xpath('./div[@class="text_box"]/h4/a/text()').extract_first()
            splits =  str(detail_url).split("/")
            out_id = splits[len(splits) - 1][0:-5]
            conver_url = data.xpath('./div[@class="picture"]/a/img/@src').extract_first()
            yield Request(
                url=detail_url,
                meta={"id": out_id,
                      "title": title,
                      "conver_url": conver_url},
                callback = self.detail
            )

    def detail(self, response):
        # out_id =response.meta.get('id')
        id = response.meta.get('id')
        cover = response.meta.get('conver_url')
        title = response.meta.get('title')
        month = response.xpath('//div[@class="article_info"]/span[@class="date"]/text()').extract_first()
        times = response.xpath('//div[@class="article_info"]/span[@class="time"]/text()').extract_first()
        published_at =str(month)+" "+str(times)
        content = response.xpath(
            "/html/body").extract_first()

        new_type = "人工智能"


        # print(
        #     id,
        #     published_at,
        #     title,
        #     new_type,
        #     "量子位",
        #     None,
        #     # content,
        #     response.url,
        #     "100",
        #     cover
        # )


        self.insert_new(
            id,
            published_at,
            title,
            new_type,
            "量子位",
            None,
            content,
            response.url,
            "100"
        )

        # self.insert_new_1(
        #     id,
        #     published_at,
        #     title,
        #     new_type,
        #     "量子位",
        #     None,
        #     content,
        #     response.url,
        #     "100",
        #     cover
        # )
        pass

