from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
from scrapy import Request
import re
from util.RegExUtil import remove
"""
互动吧 ===== 金融  科技 互联网  医疗 路演
"""


class HdbSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdb_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["hdb.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.hdb.com/quanguo/{active_type}/'
    active_types = [
        {"name": "金融", "value": "35-108-0-2-0-0-1"},
        {"name": "科技", "value": "194-108-0-2-0-0-1"},
        {"name": "互联网", "value": "24-101-0-2-0-0-1"},
        {"name": "路演", "value": "34-110-0-2-0-0-1"},
        {"name": "医疗", "value": "69-108-0-2-0-0-1"}
    ]

    def __init__(self, *a, **kw):
        super(HdbSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for active_type in self.active_types:
            yield Request(
                self.start_urls.format(active_type=active_type.get("value")),
                meta=active_type,
                dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//ul[@class="find_main_ul dataViewClass"]/li[@class="find_main_li img find"]')
        classify =response.meta["name"]
        if data_list is not None:
            for data in data_list:
                detail_url = data.xpath('./div[@class="find_main_div"]/h3[@class="find_main_title"]/a/@href').extract_first()
                title = data.xpath('./div[@class="find_main_div"]/h3[@class="find_main_title"]/a/text()').get().strip()
                place = data.xpath('./div[@class="find_main_div"]/div[@class="find_main_fixH"]/div[@class="find_main_address"]/p/a/text()').extract_first()
                yield Request(
                    detail_url,
                    meta={
                        "place": place,
                        "title": title,
                        "classify": classify,
                        "detail_url": detail_url
                    },
                    callback=self.detail

                )
        # 获取下一页
        next_url = response.xpath('//div[@class="join_feny"]/a[last()]/@href').extract_first()

        if next_url is not None:
            strs = str(next_url).split('-')
            num = strs[len(strs) - 1][0:-1]
            if int(num) <= 50:
                yield Request(
                    next_url,
                    dont_filter=True,
                    meta=response.meta,
                    callback=self.parse

                )
            else:
                return
        else:
            return

    def detail(self, response):
        source = "互动吧"
        tag = None
        place = response.meta['place']
        classify = response.meta['classify']
        link = response.meta['detail_url']
        title = response.xpath('/html/head/title/text()').extract_first()
        title = remove(u'[\U00010000-\U0010ffff]', title)
        description = response.xpath('/html/head/meta[@name="description"]/@content').extract_first()
        sub = "。马上报名参加"
        times = str(description).split('活动时间：')[1].split(sub)[0]
        suffer = times[0:4]
        if suffer != "2018" and suffer != "2019":
            times = "2018-"+times
        self.insert_new(
            title,
            times,
            place,
            tag,
            classify,
            link,
            source
        )
