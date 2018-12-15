from dyly_spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request, FormRequest
import time
import scrapy


class IheimaSpider(ActiveSpider):
    name = "iheima_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["iheima.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://www.iheima.com/hmactivity/pages?page={pageNo}&pagesize=10'
    base_url = "http://www.iheima.com"

    def __init__(self, *a, **kw):
        super(IheimaSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_urls.format(pageNo=1),
            meta={"page": "1"}

        )

    def parse(self, response):
        data_json = json.loads(response.text)
        datas = data_json['data']
        if datas is not None and len(datas) != 0:
            datas = datas['list']
            if datas is not None and len(datas) != 0:
                for data in datas:
                    title = data['title']
                    place = data['address']
                    link = data['url']
                    times = data['activity_time']
                    times = str(times).replace(r'～ ', '～ ').replace(r' ～ ', '～ ').replace(r'~', '～ ')
                    times = str(times).split('～ ')[0]
                    times = times.split('-')[0]
                    suffer = times[0:2]
                    if suffer != '20':
                        times = "2018年"+times
                    times = str(times).replace(r',', '-').replace(r'.', '-').replace(r'年', '-').replace(r'月', '-').replace(r'日', ' ')
                    classify = "活动"
                    source = "i黑马网"
                    self.insert_new(
                        title,
                        times,
                        place,
                        None,
                        classify,
                        link,
                        source
                    )
                # page = response.meta["page"]
                # next_page = int(page) + 1
                # yield Request(
                #     self.start_urls.format(pageNo=next_page),
                #     meta={"page": str(next_page)}
                #
                # )
            else:
                return
