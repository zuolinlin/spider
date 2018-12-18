from dyly_spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
"""
环球科技 =====互联网，5G/通信,智能（人工智能，VR/AR，汽车，物联网，智慧城市，智能生产），双创
"""


class HuanqiuSpider(NewsSpider):
    name = "huanqiu_news"
    allowed_domains = ["huanqiu.com"]
    #  开始爬取的地址  按照行业分类来爬取

    base_url = "http://{suffer}.huanqiu.com/{type}/"
    news_types = [
        {"name": "互联网", "value": "internet"},
        {"name": "5G/通讯", "value": "comm"},
        {"name": "双创", "value": "business"},
        {"name": "人工智能", "value": "ai"},
        {"name": "VR/AR", "value": "vr"},
        {"name": "汽车", "value": "travel"},
        {"name": "物联网", "value": "iot"},
        {"name": "智慧城市", "value": "city"},
        {"name": "智能成产", "value": "product"}
    ]

    def __init__(self, *a, **kw):
        super(HuanqiuSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.news_types:
            if news_type.get("value") == "internet" or news_type.get("value") == "comm" or news_type.get("value") == "business":
                yield Request(
                    self.base_url.format(suffer="tech", type=news_type.get("value")),
                    meta=news_type,
                    dont_filter=True
                )
            else:
                yield Request(
                    self.base_url.format(suffer="smart", type=news_type.get("value")),
                    meta=news_type,
                    dont_filter=True
                )

    def parse(self, response):
        data_list = response.xpath('//div[@class="fallsFlow"]/ul/li')
        if data_list is not None:
            for data in data_list:
                href = data.xpath('./h3/a/@href').extract_first()
                yield Request(
                    href,
                    meta=response.meta,
                    callback=self.detail
                )
        # 获取下一页的数据
        next_page = response.xpath('//div[@id="pages"]/a[last()]/@href').extract_first()
        yield Request(
            next_page,
            meta=response.meta,
            callback=self.parse
        )

    def detail(self, response):
        title = response.xpath('//div[@class="l_a"]/h1/text()').extract_first()
        push_time = response.xpath('//div[@class="l_a"]/div[@class="la_tool"]/span/text()').extract_first()
        content = response.xpath('//div[@class="l_a"]/div[@class="la_con"]').extract_first()
        source = "环球网"
        strs = str(response.url).split('/')
        out_id = strs[len(strs) -1][0:-5]
        new_type = response.meta['name']
        spider_source = 59
        digest = None
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

