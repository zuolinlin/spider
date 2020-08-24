
from spider.spiders.active.ActiveSpider import ActiveSpider
import json
from scrapy import Request
import scrapy

"""
第一财经大直播
"""


class YicaiSpider(ActiveSpider):
    name = "yicai_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["smgbb.cn"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://yicai.smgbb.cn/api/ajax/getlivelist?cid=516&pagesize=10&page={pageNo}&type=2'
    base_url = "https://yicai.smgbb.cn"

    def __init__(self, *a, **kw):
        super(YicaiSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            url=self.start_urls.format(pageNo=1),
            meta={"pageNo": "1"}
        )

    def parse(self, response):
        data_text = response.text
        datas = json.loads(data_text)
        if datas is not None and len(datas) != 0:
            for data in datas:
                times = data['LiveDate']
                title = data['NewsTitle']
                url = data['url']
                link = self.base_url + url
                source = "第一财经"
                self.insert_new(
                    title,
                    times,
                    None,
                    None,
                    None,
                    link,
                    source
                )
            # pageNo = response.meta['pageNo']
            # next_page = int(pageNo) + 1
            # yield scrapy.FormRequest(
            #     url=self.start_urls.format(pageNo=next_page),
            #     meta={"pageNo": next_page},
            #     callback=self.parse
            # )
        else:
            return
