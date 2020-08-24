from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json
from util.XPathUtil import str_to_selector

"""
中国网 ===、 金融、证劵、科技、医疗、消费、区块链、能源、

"""


class ChinaSpider(NewsSpider):
    name = "china_news"
    allowed_domains = ["china.com.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    base_url = "http://app.{type}.china.com.cn/news/more_news.php?cnl={news_type}&callback=jQuery111106981507309942452_1544061033459&index=0&page={page}"

    new_types =[
        {"name": "金融","value": "money"},
        {"name": "证劵","value": "stock"},
        {"name": "科技","value": "tech"},
        {"name": "消费", "value": "consume"},
        {"name": "医疗", "value": "medicine"},
        {"name": "区块链", "value": "bc"},
        {"name": "能源", "value": "energy"}
    ]

    def __init__(self, *a, **kw):
        super(ChinaSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for news_type in self.new_types:
            # 区块链和科技
            if news_type["value"] == "tech" or news_type["value"] == "bc":
                yield Request(
                         self.base_url.format(type="tech", news_type=news_type.get("value"), page=1),
                         meta=news_type,
                         dont_filter=True
                )
            else:
                yield Request(
                        self.base_url.format(type="finance", news_type=news_type.get("value"), page=1),
                        meta=news_type,
                        dont_filter=True
                )

    def parse(self, response):
        text= response.text

        text =str(text).replace('jQuery111106981507309942452_1544061033459(', "")[0:-1]
        if text is not None:
           datas = json.loads(text)
           for data in datas:
               data_selector = str_to_selector(data)
               detail_url = data_selector.xpath('//li/h3/a/@href').extract_first()
               yield Request(
                   detail_url,
                   meta=response.meta,
                   callback=self.detail
               )
        # # 获取下一页的新闻页的数据
        # url = response.url
        # page =str(url).split("&page=")[1]
        # next_page_num = int(page) + 1
        # next_page_url = str(url).split("&page=")[0]+"&page=" + str(next_page_num)
        # yield Request(
        #     next_page_url,
        #     meta=response.meta,
        #     dont_filter=True,
        #     callback=self.parse
        # )

    def detail(self, response):
        new_type = response.meta['name']
        title = response.xpath('//div[@class="wrap c top"]/h1/text()').extract_first()
        push_time = response.xpath('//span[@class="fl time2"][1]/text()').get().strip()
        push_time = str(push_time).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
        source = response.xpath('//span[@class="fl time2"]/a/text()').extract_first()
        if source is None:
            source = response.xpath('//span[@class="fl time2"][1]/text()').extract_first()
            source = str(source).split('  ')[1]
        url = response.url
        strs = str(url).split("/")
        out_id = strs[len(strs) -1][0:-6]
        content = response.xpath('//div[@class="navp c"]').extract_first()

        # print(out_id, push_time, title, new_type, source, response.url)
        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            None,
            content,
            response.url,
            47
        )
