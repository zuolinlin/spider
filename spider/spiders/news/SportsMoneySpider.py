from scrapy import Request

from spider.spiders.news.NewsSpider import NewsSpider

"""
体育大生意：资讯（全部），深度（深度，创投，产研，政策）

"""


class SportsMoneySpider(NewsSpider):
    name = "sport_money_news"

    allowed_domains=["sportsmoney.cn"]

    start_url = "http://www.sportsmoney.cn"

    news_type_list = [
        {"category": "zuqiu", "name": "足球"},
        {"category": "lanqiu", "name": "篮球"},
        {"category": "aoyun", "name": "奥运"},
        {"category": "bingxue", "name": "冰雪"},
        {"category": "dianjing", "name": "电竞"},
        {"category": "jianshen", "name": "健身"},
        {"category": "lupao", "name": "路跑"},
        {"category": "boji", "name": "搏击"},
        {"category": "peixun", "name": "培训"},
        {"category": "qiche", "name": "汽车运动"},
        {"category": "shendu", "name": "深度"},
        {"category": "chuangke", "name": "创投"},
        {"category": "chanyan", "name": "产研"},
        {"category": "zhengce", "name": "政策"},
    ]

    #数据列表
    list_url = "http://www.sportsmoney.cn/{category}/p{page}.html"

    #数据详情
    detail_url = "http://www.sportsmoney.cn/article/{id}.html"

    def __init__(self, *a, **kw):
        super(SportsMoneySpider, self).__init__(*a, **kw)

    def start_requests(self):
        page = 1
        for news_type in self.news_type_list:
            yield Request(
                self.list_url.format(page=page, category=news_type.get("category")),
                meta=news_type,
                dont_filter=True,
                callback=self.parse
            )

    def parse(self, response):
        data_list = response.xpath('//div[@class="row news-list zixun"]/div[@class="col-sm-4 news-item"]')
        for data in data_list:
            #新闻详情url地址
            detailurl = str(data.xpath('./div/div/a/@href').extract_first())
            #新闻主标题
            title = str(data.xpath('./div/div[@class="article-title article-title-wp"]/a/text()').extract_first())

            #外部编号
            strs = str(detailurl).split('/')
            out_id = strs[strs.__len__() - 1].split('.')[0]

            yield Request(
                url=self.start_url+detailurl,
                meta={
                    "title": title,
                    "out_id": out_id,
                    "new_type": response.meta['name']
                },
                dont_filter=True,
                callback=self.detail
            )

    def detail(self, response):
        push_date = response.xpath('//div[@class="content-left"]/div[@class="news-v-info"]/span[@class="news-tag '
                                   'ml20"]/text()').extract_first()
        digest = response.xpath('//div[@class="content-left"]/div[@class="article-quote '
                                'mt20"]/text()').extract_first()
        content = response.xpath('//div[@class="content-left"]/div[@class="news-content view mt30"]').extract_first()

        out_id = response.meta['out_id']
        title = response.meta['title']
        new_type = response.meta['new_type']
        source = '体育大生意'
        source_url = response.url
        spider_source = 108

        # print(out_id, push_date, title, new_type, source, digest, source_url, spider_source)
        self.insert_new(
            out_id,
            push_date,
            title,
            new_type,
            source,
            digest,
            content,
            source_url,
            spider_source
        )