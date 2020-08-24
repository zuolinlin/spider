
from spider.spiders.news.NewsSpider import NewsSpider
from scrapy import Request, signals
import scrapy
import json
import time

"""
  VR陀螺
"""
class VRTuoLuoSpider(NewsSpider):
    name = "vrtuoluo_news"
    allowed_domains = ["https://www.vrtuoluo.cn/"]

    start_urls = ['https://www.vrtuoluo.cn/api/post/list?page={n}&limit=15'.format(n = n) for n in range(1, 2)]
    base_url = 'https://www.vrtuoluo.cn/'


    def __init__(self, *a, **kw):
        super(VRTuoLuoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for start_url in self.start_urls:
            yield scrapy.FormRequest(
                start_url
            )

    def parse(self, response):
        data_json = json.loads(response.body.decode('utf-8'))
        data_list = data_json['data']['data']
        # print(data_list)

        for data in data_list:
            # print(data['aid'])
            out_id = data['aid']
            push_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['createline']))
            title = data['title']
            new_type = data['categories'][0]
            source = 'VR陀螺'
            digest = data['dis']
            content = data['content']
            source_url = self.base_url + str(data['aid']) + '.html'
            spider_source = 62


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
            self.insert_new(
                out_id,
                push_time,
                title,
                new_type,
                source,
                digest,
                content,
                source_url,
                spider_source
            )


        pass

    def detail(self, response):
        pass
