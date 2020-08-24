import re
import time
import json

from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
from urllib import parse
"""
环球科技 =====互联网，5G/通信,智能（人工智能，VR/AR，汽车，物联网，智慧城市，智能生产），双创
"""


class HuanqiuSpider(NewsSpider):
    name = "huanqiu_news"
    allowed_domains = ["huanqiu.com"]
    #  开始爬取的地址  按照行业分类来爬取

    start_urls1 = ["https://tech.huanqiu.com/api/list?node=%22/e3pmh164r/e3pmh2hq8%22,%22/e3pmh164r/e3pmh33i9%22,%22/e3pmh164r/e3pmh356p%22,%22/e3pmh164r/e3pmh3dh4%22,%22/e3pmh164r/e3pmtlao3%22,%22/e3pmh164r/e3pmtm015%22,%22/e3pmh164r/e3pmtnh4j%22,%22/e3pmh164r/e3pn1fd3s%22,%22/e3pmh164r/e3pn46ri0%22,%22/e3pmh164r/e3pn4bn46%22,%22/e3pmh164r/e3pn4gh77%22,%22/e3pmh164r/e3pn4qlss%22,%22/e3pmh164r/e3pn6fo08%22,%22/e3pmh164r/e3ptqlvrg%22&offset={n}&limit=20".format(n = n) for n in range(0, 20, 20)]
    start_urls2 = ["https://smart.huanqiu.com/api/list?node=%22/e3pmh140m/e3pmh14i1%22,%22/e3pmh140m/e3pmh2jgm%22,%22/e3pmh140m/e3pmh31se%22,%22/e3pmh140m/e3pmh4huv%22,%22/e3pmh140m/e3pmh4huv/e3pmh4ign%22,%22/e3pmh140m/e3pn62ehj%22,%22/e3pmh140m/e3pn7fsu3%22,%22/e3pmh140m/e5arbmudl%22,%22/e3pmh140m/e7qeadr4p%22,%22/e3pmh140m/e7qeal82i%22,%22/e3pmh140m/e7qeaudr2%22,%22/e3pmh140m/e7qeb3iev%22,%22/e3pmh140m/e7qeb8nre%22,%22/e3pmh140m/e7qebdhuc%22&offset={n}&limit=20".format(n = n) for n in range(0, 20, 20)]
    start_urls3 = ["https://finance.huanqiu.com/api/list?node=%22/e3pmh1hmp/e3pmh1iab%22,%22/e3pmh1hmp/e3pn46htn%22,%22/e3pmh1hmp/e3pn60gdi%22,%22/e3pmh1hmp/e3pn60gdi/e3pn60h31%22,%22/e3pmh1hmp/e3pn60gdi/e3pru2fi2%22,%22/e3pmh1hmp/e3pn60rs2%22,%22/e3pmh1hmp/e3pn60rs2/e3pn60skq%22,%22/e3pmh1hmp/e3pn60rs2/e3ptlr015%22,%22/e3pmh1hmp/e3pn61831%22,%22/e3pmh1hmp/e3pn61an9%22,%22/e3pmh1hmp/e3pn61chp%22,%22/e3pmh1hmp/e3pn62ihu%22,%22/e3pmh1hmp/e3pn62uuq%22,%22/e3pmh1hmp/e3pn6314j%22,%22/e3pmh1hmp/e3pn6314j/e3pn6323a%22,%22/e3pmh1hmp/e3pn6314j/e3ptma9ah%22,%22/e3pmh1hmp/e3ptkencb%22,%22/e3pmh1hmp/e3ptlrdc9%22,%22/e3pmh1hmp/e3ptlrdc9/e3ptltkc2%22,%22/e3pmh1hmp/e3ptlrdc9/e3ptm2ci2%22,%22/e3pmh1hmp/e7i6qafud%22,%22/e3pmh1hmp/e7i6t8c0j%22,%22/e3pmh1hmp/e7lipkhq1%22,%22/e3pmh1hmp/e7lipkhq1/e7lipkii0%22,%22/e3pmh1hmp/e7lipkhq1/e7o08h1r8%22&offset={n}&limit=20".format(n = n) for n in range(0, 20, 20)]

    start_urls = start_urls1 + start_urls2 + start_urls3

    def __init__(self, *a, **kw):
        super(HuanqiuSpider, self).__init__(*a, **kw)

    def start_requests(self):
        # print('开始')
        for start_url in self.start_urls:
            # print('---->', start_url)
            yield Request(
                start_url,
                callback=self.parse
            )

    def parse(self, response):
        data = response.text
        if data is not None:
            jsondata = json.loads(data)
            items = jsondata['list']
            for item in items:
                try:
                    out_id = item['aid']
                    title = item['title']

                    new_type = re.findall(r'https://(.*?)\.', response.url)[0]
                    if new_type == 'tech':
                        new_type = '科技'
                    elif new_type == 'smart':
                        new_type = '智能'
                    elif new_type == 'finance':
                        new_type = '财经'

                    source = item['source']['name']
                    push_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(item['ctime'][:10])))
                    detial_url = item['source']['url']
                    digest = item['summary']

                except Exception as e:
                    # print(e)
                    continue
                else:
                    if detial_url is None:
                        continue
                    else:
                        yield Request(
                            detial_url,
                            meta={"out_id": out_id,
                                  "push_time": push_time,
                                  "title": title,
                                  "new_type": new_type,
                                  "source": source,
                                  "digest": digest,
                                  },
                            callback=self.detail,
                            dont_filter=True
                        )

    def detail(self, response):
        try:
            out_id = response.meta['out_id']
            push_time = response.meta['push_time']
            title = response.meta['title']
            new_type = response.meta['new_type']
            source = response.meta['source']
            digest = response.meta['digest']
            content = response.xpath("/html/body").extract_first()
            source_url = response.url
            spider_source = 59
            # print(
            #     out_id,
            #     push_time,
            #     title,
            #     new_type,
            #     source,
            #     digest,
            #     # content,
            #     source_url,
            #     spider_source
            # )
        except Exception as e:
            print(e)
        else:
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

