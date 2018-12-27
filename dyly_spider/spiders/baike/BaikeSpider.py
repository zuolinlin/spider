from dyly_spider.spiders.BaseSpider import BaseSpider
import json
from scrapy import Request
import uuid

class BaikeSpider(BaseSpider):
    name = "baike"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["baike.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'http://www.baike.com/category/Ajax_cate.jsp?catename={catename}'

    def __init__(self, *a, **kw):
        super(BaikeSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield Request(
            self.start_urls.format(catename="页面总分类"),
            meta={"parentId": "0"}
        )

    def parse(self, response):

        text = response.text
        data_list = json.loads(text)
        if data_list is not None and len(data_list) != 0:
            for data in data_list:
                parent_id = response.meta['parentId']
                params = []

                classify_name = data['name']
                id = data['id']

                params.append((
                    id,
                    classify_name,
                    parent_id
                ))
                self.insert("""
                                INSERT INTO `baike_classify` (
                                  `id`,
                                  
                                  `classify_name`,
                                  `parent_id`
                                )
                                VALUES (%s, %s, %s)
                                """, params)

                yield Request(
                    self.start_urls.format(catename=classify_name),
                    meta={"parentId": id}
                )





