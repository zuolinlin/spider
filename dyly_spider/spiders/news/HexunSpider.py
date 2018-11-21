import json
import jsonpath
import scrapy
import time
from scrapy.http.response.html import HtmlResponse
from dyly_spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from util.XPathUtil import str_to_selector
from dyly_spider.spiders.news.NewsSpider import NewsSpider


class HexunSpider(NewsSpider):

    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "hexun"
    allowed_domains = ["hexun.com"]
    # 金融与资本市场
    start_urls = ["http://news.hexun.com/financial/"]

    request_url ="http://open.tool.hexun.com/MongodbNewsService/newsListPageByJson.jsp?id=100018982&s=30&cp={}&priority=0&callback=hx_json31542624833618"

    def __init__(self, *a, **kw):
        super(HexunSpider, self).__init__(*a, **kw)
        self.current_page = 1
        self.browser = None

    def start_requests(self):
        url = "http://open.tool.hexun.com/MongodbNewsService/newsListPageByJson.jsp?id=100018982&s=30&cp=1&priority=0&callback=hx_json31542624833618"
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.Request(
            url=url,
            dont_filter=True,
            callback=self.parse
        )

    def parse(self, response):
        html = response.text
        if html is not None:
            # 15146
            pages = 15146
            # 根据返回的totalNumber 计算出来的总页书有误 实际的数量 15146
            while self.current_page < pages:
                self.current_page = self.current_page + 1
                next_url = "http://open.tool.hexun.com/MongodbNewsService/newsListPageByJson.jsp?id=100018982&s=30&cp=" + str(
                self.current_page) + "&priority=0&callback=hx_json31542624833618"
                yield Request(next_url, dont_filter=True, callback=self.parse)
            time.sleep(3)
            jsonData = str(html)[22:-4]
            datas = json.loads(jsonData)
            result = datas['result']
            for data in result:
                entitytime = data['entitytime']  # 时间
                entityurl = data['entityurl']   # url
                out_id = data['id']            # id
                title = data['title']         # 标题
                yield Request(
                        entityurl,
                        meta={"entitytime": entitytime,
                              "out_id": out_id,
                              "title": title},
                        callback=self.detail
                )

    def detail(self, response):
        out_id = response.meta['out_id']
        title = response.meta['title']
        new_type = "金融与资本市场"
        digest = None
        spider_source = "7"
        #  和讯网额新闻页详情对应的是三套模版
        # 最新的一套模版
        articleTopBg = response.xpath('/html/body/div[@class="articleTopBg"]')
        if articleTopBg is not None and len(articleTopBg) != 0:
            push_data = response.xpath('/html/body/div[@class="layout mg articleName"]/div/div[1]/span/text()').get().strip()
            source = response.xpath('/html/body/div[@class="layout mg articleName"]/div/div[1]/a/text()').get().strip()
            content = response.xpath('//div[@class="art_contextBox"]//p//text()').getall()
            content = "".join(content).strip()
        # 详情页的 第二套模版
        subnav = response.xpath('//div[@id="wrap"]/div[@class="subnav"]')
        if subnav is not None and len(subnav) != 0:
            push_data = response.xpath(
                '//div[@id="artibodyTitle"]/div[1]/span[@class="gray"]/text()').get().strip()
            push_data = str(push_data).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
            source = "和讯网"
            content = response.xpath('//div[@id="artibody"]//p//text()').getall()
            content = "".join(content).strip()
        # 详情页的第三套模版
        standStockPanel = response.xpath('//div[@id="standStockPanel"]')
        if standStockPanel is not None and len(standStockPanel) != 0:
            push_data = response.xpath(
                '//div[@id="artibodyTitle"]/div[1]/div[1]/span[@class="gray"]/text()').get().strip()
            push_data = str(push_data).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
            source = "和讯网"
            content = response.xpath('//div[@id="artibody"]//p//text()').getall()
            content = "".join(content).strip()
        # 详情页的第四套模版
        navetc = response.xpath('//div[@id="navetc"]')
        if navetc is not None and len(navetc) != 0:
            push_data = response.xpath(
                '//div[@id="mainbox"]/div[2]/div[1]/font/text()').get().strip()
            push_data = str(push_data).replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
            source = "和讯网"
            content = response.xpath('//div[@class="detail_cnt"]//p//text()').getall()
            content = "".join(content).strip()
        self.insert_new(
            out_id,
            push_data,
            title,
            new_type,
            source,
            digest,
            content,
            spider_source
        )
