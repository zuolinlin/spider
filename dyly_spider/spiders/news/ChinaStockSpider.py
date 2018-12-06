from dyly_spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import json
from util.XPathUtil import str_to_selector

"""
中国网 ===  新三板

"""


class ChinaStockSpider(NewsSpider):
    name = "china_stock_news"
    allowed_domains = ["china.com.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    base_url = "http://app.finance.china.com.cn/news/column.php?cname=新三板&p={page}"

    def __init__(self, *a, **kw):
        super(ChinaStockSpider, self).__init__(*a, **kw)

    def start_requests(self):

            yield Request(
                    self.base_url.format(page=80),
                    meta={"new_type": "新三板"},
                    dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//ul[@class="news_list"]/li')
        new_type =response.meta["new_type"]
        if data_list is not None:
            for data in data_list:
                detail_url = data.xpath('./a/@href').extract_first()
                suffer = str(detail_url)[-5:]
                if suffer == "shtml":
                    push_data =data.xpath('./span/text()').extract_first()
                    yield Request(
                        detail_url,
                        meta={
                            "push_data": push_data,
                            "new_type": new_type
                        },
                        callback=self.detail
                    )
        url = response.url
        page = str(url).split("&p=")[1]
        next_page_num = int(page) + 1
        if next_page_num <= 86:
            next_page_url = str(url).split("&p=")[0] + "&p=" + str(next_page_num)
            yield Request(
                next_page_url,
                meta=response.meta,
                dont_filter=True,
                callback=self.parse
            )

    def detail(self, response):
        new_type = response.meta['new_type']
        push_time = response.meta['push_data']
        url = response.url
        strs = str(url).split("/")
        out_id = strs[len(strs) - 1][0:-6]
        title = response.xpath('//div[@class="wrap c top"]/h1/text()').extract_first()
        if title is not None:
            source = response.xpath('//span[@class="fl time2"]/a/text()').extract_first()
            if source is None:
                source = response.xpath('//span[@class="fl time2"][1]/text()').extract_first()
                source = str(source).split('  ')[1]

            content = response.xpath('//div[@class="navp c"]').extract_first()
        else:
            title = response.xpath('//div[@class="left_content"]/h1/text()').extract_first()
            source = response.xpath('//span[@id="source_baidu"]/a/text()').extract_first()
            # content = ""
            content = response.xpath('//div[@class="tex"]').extract_first()
            # for cnt in contents:
            #     ct = cnt.xpath('./p[@align="center"]')
            #     if ct is None or len(ct) == 0:
            #         cnt = cnt.extract_first()
            #         content += str(cnt)
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
